import re
import math
import logging
from aiohttp import web
from stream.utils import ByteStreamer, render_template, humanbytes, FileNotFound

routes = web.RouteTableDef()
streamers = {}

def get_streamer(bot):
    if bot not in streamers:
        streamers[bot] = ByteStreamer(bot)
    return streamers[bot]

@routes.get('/stream/{token}/{filename}')
async def stream_handler(request: web.Request):
    bot = request.app['bot']
    
    if not bot.stream_mode:
        return web.HTTPNotFound(text="Streaming is disabled")
    
    token = request.match_info['token']
    filename = request.match_info['filename']
    
    token_data = await bot.mongodb.validate_stream_token(token)
    if not token_data:
        return web.HTTPNotFound(text="Invalid or expired link")
    
    user_id = token_data['user_id']
    if not await bot.mongodb.is_premium(user_id):
        return web.HTTPForbidden(text="Premium required")
    
    channel_id = token_data['channel_id']
    msg_id = token_data['msg_id']
    
    range_header = request.headers.get('Range', None)
    streamer = get_streamer(bot)
    
    try:
        file_props = await streamer.get_file_properties(channel_id, msg_id)
    except FileNotFound:
        return web.HTTPNotFound(text="File not found")
    
    file_size = file_props.file_size
    
    if range_header:
        match = re.search(r'bytes=(\d+)-(\d*)', range_header)
        if match:
            from_bytes = int(match.group(1))
            until_bytes = match.group(2)
            until_bytes = int(until_bytes) if until_bytes else file_size - 1
        else:
            from_bytes = 0
            until_bytes = file_size - 1
    else:
        stream_url = f"/stream/{token}/{filename}"
        template = 'req.html' if file_props.mime_type and file_props.mime_type.startswith('video') else 'dl.html'
        html = await render_template(
            template,
            file_name=file_props.file_name,
            file_url=stream_url,
            file_size=humanbytes(file_size)
        )
        return web.Response(text=html, content_type='text/html')
    
    if from_bytes < 0 or until_bytes >= file_size or until_bytes < from_bytes:
        return web.Response(
            status=416,
            headers={'Content-Range': f'bytes */{file_size}'}
        )
    
    chunk_size = 1024 * 1024
    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1
    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)
    
    body = streamer.yield_file(
        channel_id, msg_id, offset,
        first_part_cut, last_part_cut,
        part_count, chunk_size
    )
    
    mime = file_props.mime_type or 'application/octet-stream'
    return web.Response(
        status=206,
        body=body,
        headers={
            'Content-Type': mime,
            'Content-Range': f'bytes {from_bytes}-{until_bytes}/{file_size}',
            'Content-Length': str(req_length),
            'Content-Disposition': f'inline; filename="{file_props.file_name}"',
            'Accept-Ranges': 'bytes'
        }
    )

@routes.get('/health')
async def health_check(request: web.Request):
    bot = request.app['bot']
    return web.json_response({
        'status': 'ok',
        'stream_mode': bot.stream_mode,
        'uptime': str(bot.uptime) if hasattr(bot, 'uptime') else 'unknown'
    })
