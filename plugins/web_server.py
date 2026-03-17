# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

from aiohttp import web
import os
import mimetypes
from datetime import datetime
from config import STREAM_BASE_URL

# This will be set by bot.py on startup
current_bot = None

async def stream_handler(request):
    """Handle streaming requests for premium users."""
    token = request.query.get('token')
    if not token:
        return web.Response(text='Missing token', status=400)

    # Get token from DB
    token_data = await current_bot.mongodb.get_streaming_token(token)
    if not token_data:
        return web.Response(text='Invalid or expired token', status=403)

    user_id = token_data['user_id']
    # Check if user is still premium
    if not await current_bot.mongodb.is_premium(user_id):
        return web.Response(text='Premium required', status=403)

    channel_id = token_data['channel_id']
    msg_id = token_data['msg_id']

    try:
        # Fetch the message from the database channel
        msg = await current_bot.get_messages(channel_id, msg_id)
    except Exception as e:
        return web.Response(text='File not found', status=404)

    # Determine file_id, mime type, size, and filename
    file_id = None
    mime = None
    file_size = None
    filename = None

    if msg.video:
        file_id = msg.video.file_id
        mime = msg.video.mime_type or 'video/mp4'
        file_size = msg.video.file_size
        filename = f"video_{msg_id}.mp4"
    elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith('video/'):
        # Check for common video extensions
        doc_name = msg.document.file_name or ''
        if doc_name.lower().endswith(('.mkv', '.mp4')):
            file_id = msg.document.file_id
            mime = msg.document.mime_type or 'video/mp4'
            file_size = msg.document.file_size
            filename = doc_name or f"file_{msg_id}"
    else:
        return web.Response(text='Not a supported video file', status=400)

    if not file_id:
        return web.Response(text='Cannot retrieve file', status=500)

    # Prepare streaming headers
    headers = {
        'Content-Type': mime,
        'Content-Disposition': f'inline; filename="{filename}"',
        'Accept-Ranges': 'bytes',
    }

    # Handle Range header (for seeking)
    range_header = request.headers.get('Range')
    start = 0
    end = file_size - 1

    if range_header:
        # Parse Range: bytes=start-end
        try:
            _, range_val = range_header.strip().split('=')
            if '-' in range_val:
                start_str, end_str = range_val.split('-')
                if start_str:
                    start = int(start_str)
                if end_str:
                    end = int(end_str)
        except:
            pass

        if start >= file_size:
            return web.Response(status=416, text='Range not satisfiable')

        headers['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        headers['Content-Length'] = str(end - start + 1)
        status = 206
    else:
        headers['Content-Length'] = str(file_size)
        status = 200

    # Stream the file using Pyrogram's get_file (returns iterator of chunks)
    response = web.StreamResponse(status=status, headers=headers)
    await response.prepare(request)

    try:
        # client.get_file returns async generator of chunks
        async for chunk in current_bot.get_file(file_id, offset=start, limit=(end - start + 1)):
            await response.write(chunk)
    except Exception as e:
        # Client disconnected or other error – just stop writing
        pass
    finally:
        await response.write_eof()

    # Optionally delete token after first use (if one-time streaming desired)
    # await current_bot.mongodb.delete_streaming_token(token)

    return response

async def home_handler(request):
    """Optional home page."""
    return web.Response(text="Streaming server is running.")

async def web_server():
    """Create and return the aiohttp web application."""
    app = web.Application()
    app.router.add_get('/', home_handler)
    app.router.add_get('/stream', stream_handler)
    return app
