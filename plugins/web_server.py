import os
import aiohttp.web as web
from aiohttp.web import RouteTableDef, Response, StreamResponse
import mimetypes

routes = RouteTableDef()
BOT = None

def setup(bot):
    global BOT
    BOT = bot

@routes.get('/')
async def index(request):
    return web.Response(text="File Stream Bot is running.")

@routes.get('/stream/{token}')
async def stream_page(request):
    token = request.match_info['token']
    bot = BOT
    if not bot:
        return web.Response(text="Bot not initialized", status=500)
    
    if not bot.stream_mode:
        return web.Response(text="Streaming is disabled", status=403)
    
    token_doc = await bot.mongodb.resolve_file_token(token)
    if not token_doc:
        return web.Response(text="Invalid token", status=404)
    
    channel_id = token_doc['channel_id']
    msg_id = token_doc['msg_id']
    end_msg_id = token_doc.get('end_msg_id')
    
    if end_msg_id:
        return web.Response(text="Batch streaming not supported", status=400)
    
    try:
        msg = await bot.get_messages(channel_id, msg_id)
        if not msg or not msg.document:
            return web.Response(text="File not found", status=404)
        file_name = msg.document.file_name
    except Exception as e:
        return web.Response(text=f"Error: {e}", status=500)
    
    template_path = os.path.join(os.path.dirname(__file__), 'template', 'req.html')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html = f.read()
    except FileNotFoundError:
        return web.Response(text="Template not found", status=500)
    
    file_url = f"{bot.fqdn}/file/{token}"
    html = html.replace('{{file_name}}', file_name).replace('{{file_url}}', file_url)
    
    return web.Response(text=html, content_type='text/html')

@routes.get('/file/{token}')
async def stream_file(request):
    token = request.match_info['token']
    bot = BOT
    if not bot:
        return web.Response(text="Bot not initialized", status=500)
    
    if not bot.stream_mode:
        return web.Response(text="Streaming disabled", status=403)
    
    token_doc = await bot.mongodb.resolve_file_token(token)
    if not token_doc:
        return web.Response(text="Invalid token", status=404)
    
    channel_id = token_doc['channel_id']
    msg_id = token_doc['msg_id']
    
    try:
        msg = await bot.get_messages(channel_id, msg_id)
        if not msg or not msg.document:
            return web.Response(text="File not found", status=404)
        
        file_name = msg.document.file_name
        file_size = msg.document.file_size
        mime_type = msg.document.mime_type or 'application/octet-stream'
        
        range_header = request.headers.get('Range')
        start = 0
        end = file_size - 1
        
        if range_header:
            try:
                range_val = range_header.strip().split('=')[1]
                parts = range_val.split('-')
                start = int(parts[0])
                if parts[1]:
                    end = int(parts[1])
            except:
                pass
        
        if start > file_size - 1 or end > file_size - 1:
            return web.Response(status=416, text="Range not satisfiable")
        
        content_length = end - start + 1
        headers = {
            'Content-Type': mime_type,
            'Content-Disposition': f'inline; filename="{file_name}"',
            'Accept-Ranges': 'bytes',
        }
        status_code = 200
        if range_header:
            headers['Content-Range'] = f'bytes {start}-{end}/{file_size}'
            status_code = 206
        
        response = StreamResponse(status=status_code, headers=headers)
        await response.prepare(request)
        
        chunk_size = 1024 * 1024
        remaining = content_length
        offset = start
        while remaining > 0:
            limit = min(chunk_size, remaining)
            async for chunk in bot.get_file(msg.document.file_id, offset=offset, limit=limit):
                await response.write(chunk)
                remaining -= len(chunk)
                offset += len(chunk)
                break
        await response.write_eof()
        return response
        
    except Exception as e:
        return web.Response(text=f"Error: {e}", status=500)

async def web_server():
    app = web.Application()
    app.add_routes(routes)
    return app
