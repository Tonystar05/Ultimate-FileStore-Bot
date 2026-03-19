import math
import asyncio
import logging
import jinja2
from pathlib import Path
from typing import Dict, Optional
from pyrogram import Client, utils, raw
from pyrogram.session import Session, Auth
from pyrogram.errors import AuthBytesInvalid
from pyrogram.file_id import FileId, FileType, ThumbnailSource
from pyrogram.types import Message

# -------------------- Custom Exceptions --------------------
class InvalidHash(Exception):
    pass

class FileNotFound(Exception):
    pass

# -------------------- Human Readable Size --------------------
def humanbytes(size: int) -> str:
    if not size:
        return "0 B"
    power = 2**10
    n = 0
    labels = ["B", "KiB", "MiB", "GiB", "TiB"]
    while size > power and n < len(labels)-1:
        size /= power
        n += 1
    return f"{round(size, 2)} {labels[n]}"

# -------------------- File Properties --------------------
async def get_media_from_message(message: Message):
    for attr in ("audio", "document", "photo", "sticker", "animation", "video", "voice", "video_note"):
        media = getattr(message, attr, None)
        if media:
            return media
    return None

async def parse_file_id(message: Message) -> Optional[FileId]:
    media = await get_media_from_message(message)
    if media:
        return FileId.decode(media.file_id)

async def parse_file_unique_id(message: Message) -> Optional[str]:
    media = await get_media_from_message(message)
    if media:
        return media.file_unique_id

async def get_file_properties(client: Client, channel_id: int, msg_id: int) -> FileId:
    """Fetch file properties from a message in a channel."""
    message = await client.get_messages(channel_id, msg_id)
    if message.empty:
        raise FileNotFound("Message not found in channel")
    media = await get_media_from_message(message)
    file_id = await parse_file_id(message)
    file_unique_id = await parse_file_unique_id(message)
    if not file_id:
        raise FileNotFound("No media in message")
    setattr(file_id, "file_size", getattr(media, "file_size", 0))
    setattr(file_id, "mime_type", getattr(media, "mime_type", ""))
    setattr(file_id, "file_name", getattr(media, "file_name", ""))
    setattr(file_id, "unique_id", file_unique_id)
    return file_id

# -------------------- ByteStreamer (custom download) --------------------
class ByteStreamer:
    def __init__(self, client: Client):
        self.client = client
        self.cached_file_ids: Dict[str, FileId] = {}
        self.clean_timer = 30 * 60
        asyncio.create_task(self._clean_cache())

    async def _clean_cache(self):
        while True:
            await asyncio.sleep(self.clean_timer)
            self.cached_file_ids.clear()
            logging.debug("Stream cache cleared")

    async def get_file_properties(self, channel_id: int, msg_id: int) -> FileId:
        cache_key = f"{channel_id}_{msg_id}"
        if cache_key not in self.cached_file_ids:
            self.cached_file_ids[cache_key] = await get_file_properties(self.client, channel_id, msg_id)
        return self.cached_file_ids[cache_key]

    async def _get_media_session(self, dc_id: int) -> Session:
        media_session = self.client.media_sessions.get(dc_id)
        if media_session is None:
            if dc_id != await self.client.storage.dc_id():
                media_session = Session(
                    self.client,
                    dc_id,
                    await Auth(self.client, dc_id, await self.client.storage.test_mode()).create(),
                    await self.client.storage.test_mode(),
                    is_media=True,
                )
                await media_session.start()
                for _ in range(6):
                    exported_auth = await self.client.invoke(
                        raw.functions.auth.ExportAuthorization(dc_id=dc_id)
                    )
                    try:
                        await media_session.send(
                            raw.functions.auth.ImportAuthorization(
                                id=exported_auth.id, bytes=exported_auth.bytes
                            )
                        )
                        break
                    except AuthBytesInvalid:
                        continue
                else:
                    await media_session.stop()
                    raise AuthBytesInvalid
            else:
                media_session = Session(
                    self.client,
                    dc_id,
                    await self.client.storage.auth_key(),
                    await self.client.storage.test_mode(),
                    is_media=True,
                )
                await media_session.start()
            self.client.media_sessions[dc_id] = media_session
        return media_session

    async def _get_location(self, file_id: FileId):
        file_type = file_id.file_type
        if file_type == FileType.CHAT_PHOTO:
            if file_id.chat_id > 0:
                peer = raw.types.InputPeerUser(
                    user_id=file_id.chat_id, access_hash=file_id.chat_access_hash
                )
            else:
                if file_id.chat_access_hash == 0:
                    peer = raw.types.InputPeerChat(chat_id=-file_id.chat_id)
                else:
                    peer = raw.types.InputPeerChannel(
                        channel_id=utils.get_channel_id(file_id.chat_id),
                        access_hash=file_id.chat_access_hash,
                    )
            location = raw.types.InputPeerPhotoFileLocation(
                peer=peer,
                volume_id=file_id.volume_id,
                local_id=file_id.local_id,
                big=file_id.thumbnail_source == ThumbnailSource.CHAT_PHOTO_BIG,
            )
        elif file_type == FileType.PHOTO:
            location = raw.types.InputPhotoFileLocation(
                id=file_id.media_id,
                access_hash=file_id.access_hash,
                file_reference=file_id.file_reference,
                thumb_size=file_id.thumbnail_size,
            )
        else:
            location = raw.types.InputDocumentFileLocation(
                id=file_id.media_id,
                access_hash=file_id.access_hash,
                file_reference=file_id.file_reference,
                thumb_size=file_id.thumbnail_size,
            )
        return location

    async def yield_file(
        self,
        channel_id: int,
        msg_id: int,
        offset: int,
        first_part_cut: int,
        last_part_cut: int,
        part_count: int,
        chunk_size: int,
    ):
        file_id = await self.get_file_properties(channel_id, msg_id)
        dc_id = file_id.dc_id
        media_session = await self._get_media_session(dc_id)
        location = await self._get_location(file_id)

        current_part = 1
        try:
            r = await media_session.send(
                raw.functions.upload.GetFile(
                    location=location, offset=offset, limit=chunk_size
                )
            )
            if isinstance(r, raw.types.upload.File):
                while True:
                    chunk = r.bytes
                    if not chunk:
                        break
                    if part_count == 1:
                        yield chunk[first_part_cut:last_part_cut]
                    elif current_part == 1:
                        yield chunk[first_part_cut:]
                    elif current_part == part_count:
                        yield chunk[:last_part_cut]
                    else:
                        yield chunk

                    current_part += 1
                    offset += chunk_size
                    if current_part > part_count:
                        break

                    r = await media_session.send(
                        raw.functions.upload.GetFile(
                            location=location, offset=offset, limit=chunk_size
                        )
                    )
        except Exception as e:
            logging.error(f"Streaming error: {e}")
            raise

# -------------------- Template Rendering --------------------
async def render_template(template_name: str, **kwargs):
    template_dir = Path(__file__).parent / "templates"
    template_path = template_dir / template_name
    with open(template_path, "r", encoding="utf-8") as f:
        template = jinja2.Template(f.read())
    return template.render(**kwargs)
