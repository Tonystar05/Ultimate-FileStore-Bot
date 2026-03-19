# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

from helper.helper_func import *
from helper.credit_db import credit_db
from helper.enhanced_credit_db import EnhancedCreditDB
from helper.font_converter import to_small_caps as sc
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import humanize
import secrets
import json
import asyncio

# Import the new button functions from others.py
from plugins.others import home_buttons, home_buttons_admin

# Load credit configuration
try:
    with open("setup.json", "r") as f:
        setup_data = json.load(f)
        credit_config = setup_data[0].get("credit_config", {})
except:
    credit_config = {}


@Client.on_message(filters.command('start') & filters.private)
@force_sub
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    present = await client.mongodb.present_user(user_id)
    if not present:
        try:
            await client.mongodb.add_user(user_id)
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Error adding a user:\n{e}")

    is_banned = await client.mongodb.is_banned(user_id)
    if is_banned:
        return await message.reply(f"**{sc('You have been banned from using this bot!')}**")
    
    # Premium check
    is_premium_user = await client.mongodb.is_premium(user_id)

    # Enhanced credit system
    enhanced_db = EnhancedCreditDB(client.db_uri, client.db_name)
    credit_data = await enhanced_db.get_credits(user_id)
    user_credits = credit_data.get("balance", 0)
    
    # Check for expired credits
    await enhanced_db.check_and_remove_expired(user_id)

    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1].strip()
        except IndexError:
            return

        # ============== REFERRAL SYSTEM ==============
        if base64_string.startswith("ref_"):
            referral_code = base64_string.replace("ref_", "")
            
            if not present:
                referrer_id = await enhanced_db.apply_referral(user_id, referral_code)
                if referrer_id:
                    await message.reply(
                        f"🎉 **{sc('Welcome!')}**\n\n"
                        f"{sc('You joined using a referral link!')}\n"
                        f"{sc('When you access your first file, your referrer will earn credits!')}"
                    )
            return
            
        access_token = None
        original_base64 = base64_string
        
        # ---------------- TOKEN VERIFIED / SHORTENER SOLVED ----------------
        if "_" in base64_string:
            parts = base64_string.split("_", 1)
            if base64_string.startswith("batch_"):
                parts = base64_string.split("_")
                if len(parts) >= 3:
                     original_base64 = f"{parts[0]}_{parts[1]}"
                     access_token = parts[2]
            elif len(parts) == 2:
                original_base64 = parts[0]
                access_token = parts[1]

            if access_token:
                token_verification_enabled = await client.mongodb.get_bot_config('token_verification_enabled', True)

                if token_verification_enabled:
                    await client.mongodb.increment_token_clicks(user_id, access_token)

                    verify_result = await client.mongodb.verify_access_token(
                        user_id, access_token, original_base64
                    )
    
                    # ======================= ANTI-BYPASS LOGIC ======================
                    if verify_result == "BYPASS":
                        if user_id not in client.admins:
                            was_banned = await client.mongodb.check_and_auto_ban(user_id, max_attempts=5)
                            
                            if was_banned:
                                await message.reply(
                                    f"<blockquote>🚫 <b>{sc('you have been banned')}</b></blockquote>\n"
                                    f"<blockquote><b>{sc('reason: multiple bypass attempts detected')}</b></blockquote>\n"
                                    f"<blockquote><b>{sc('contact admin if you think this is a mistake')}</b></blockquote>"
                                )
                                return
                        
                        await message.reply(
                            f"<blockquote>⚠️ <b>{sc('bypass detected')}</b></blockquote>\n"
                            f"<blockquote><b>{sc('how many times have i told you, dont try to outsmart your dad')}🖕</b></blockquote>\n"
                            f"<blockquote><b>{sc('now be a good boy and solve it again, and this time dont get smart !!')}</b></blockquote>"
                        )
    
                        bypass_count = await client.mongodb.get_bypass_count(user_id)
                        await client.send_message(
                            client.owner,
                            f"🚨 <b>{sc('bypass detected')}</b>\n"
                            f"{sc('user')}: <code>{user_id}</code>\n"
                            f"{sc('attempts in 24h')}: <b>{bypass_count}</b>"
                        )
                        return
                    
                    if verify_result == "ALREADY_USED":
                        await message.reply(
                            f"<blockquote>❌ <b>{sc('token already used')}</b></blockquote>\n"
                            f"<blockquote><b>{sc('this link can only be used once')}</b></blockquote>\n"
                            f"<blockquote><b>{sc('please get a new link')}</b></blockquote>"
                        )
                        return
                    
                    if verify_result == "EXPIRED":
                        await message.reply(
                            f"<blockquote>⏰ <b>{sc('token expired')}</b></blockquote>\n"
                            f"<blockquote><b>{sc('this link has expired')}</b></blockquote>\n"
                            f"<blockquote><b>{sc('please get a new link')}</b></blockquote>"
                        )
                        return
    
                    if verify_result != "OK":
                        await message.reply(
                            f"<blockquote>❌ <b>{sc('invalid token')}</b></blockquote>\n"
                            f"<blockquote><b>{sc('please get a new link')}</b></blockquote>"
                        )
                        return
    
                    # ---------------- GIVE 3 CREDITS (IF ENABLED) ----------------
                    credit_system_enabled = await client.mongodb.is_credit_system_enabled()
                    
                    if credit_system_enabled:
                        expiry_days = credit_config.get("expiry_days", 30)
                        verification_reward = await client.mongodb.get_bot_config('verification_reward', 3)
                        await enhanced_db.add_credits(user_id, verification_reward, expiry_days, reason="shortener_solved")

                        credit_data = await enhanced_db.get_credits(user_id)
                        user_credits = credit_data.get("balance", 0)
    
                        await message.reply(
                            f"<b>🎉 {sc('verification successful!')}</b>\n"
                            f"✅ <b>{sc(f'you earned {verification_reward} credits!')}</b>\n"
                            f"📂 <b>{sc('sending your file now...')}</b>"
                        )
                    else:
                        await message.reply(
                            f"<b>🎉 {sc('verification successful!')}</b>\n"
                            f"📂 <b>{sc('sending your file now...')}</b>"
                        )

                    is_premium_user = True
                    
                    if original_base64.startswith("batch_"):
                         batch_id = original_base64.replace("batch_", "").strip()
                         from plugins.batch_handler import process_batch
                         await process_batch(client, message, batch_id)
                         message.stop_propagation()
                         return

        # -------------------------- HYBRID TOKEN / BASE64 DECODE --------------------------
        from helper.helper_func import is_token_format
        
        is_batch = original_base64.startswith("batch_")
        
        # Initialize variables
        ids = []
        custom_chat_id = None
        
        if not is_batch and is_token_format(original_base64):
            # ----- HYBRID TOKEN -----
            if await client.mongodb.is_token_rate_limited(user_id):
                return await message.reply(
                    f"<blockquote>⏳ <b>{sc('too many invalid attempts')}</b></blockquote>\n"
                    f"<blockquote><b>{sc('please wait a minute and try again')}</b></blockquote>"
                )
            
            token_doc = await client.mongodb.resolve_file_token(original_base64)
            
            if not token_doc:
                await client.mongodb.record_invalid_token_attempt(user_id)
                return await message.reply(
                    f"<blockquote>❌ <b>{sc('invalid or expired link')}</b></blockquote>\n"
                    f"<blockquote><b>{sc('please get a new link')}</b></blockquote>"
                )
            
            channel_id = token_doc["channel_id"]
            start_msg_id = token_doc["msg_id"]
            end_msg_id = token_doc.get("end_msg_id")
            
            if end_msg_id:
                ids = list(range(start_msg_id, end_msg_id + 1))
            else:
                ids = [start_msg_id]
                
            custom_chat_id = channel_id
            
        elif not is_batch:
            # ----- OLD BASE64 PATH -----
            try:
                string = await decode(original_base64)
                argument = string.split("-")
            except Exception:
                return
        
            if len(argument) == 3:
                # New format: get-CHANNEL_ID-MSG_ID (channel_id without -100)
                try:
                    channel_id_part = int(argument[1])
                    msg_id_part = int(argument[2])
                    custom_chat_id = int(f"-100{channel_id_part}")
                    ids = [msg_id_part]
                except:
                    # Old range format: get-ID1-ID2
                    try:
                        start = int(int(argument[1]) / abs(client.db))
                        end = int(int(argument[2]) / abs(client.db))
                        ids = list(range(start, end + 1)) if start <= end else list(range(start, end - 1, -1))
                    except:
                        return
            elif len(argument) == 2:
                # Old single file format: get-GENERATED_ID
                try:
                    msg_id = int(int(argument[1]) / abs(client.db))
                    ids = [msg_id]
                except:
                    return
            else:
                return

        # ==================== NEW: PREMIUM STREAMING MENU ====================
        # This section handles premium users and shows the streaming menu
        credit_system_enabled = await client.mongodb.is_credit_system_enabled()
        token_verification_enabled = await client.mongodb.get_bot_config('token_verification_enabled', True)
        
        is_first_file = credit_data.get("total_spent", 0) == 0 and not is_premium_user

        # If user is premium or has credits → show streaming menu
        if is_premium_user or (credit_system_enabled and user_credits > 0):
            # Handle batch links separately
            if original_base64.startswith("batch_"):
                from plugins.batch_handler import process_batch
                await process_batch(client, message, batch_id)
                return

            # Get channel and message ID
            if custom_chat_id and ids:
                channel_id = custom_chat_id
                msg_id = ids[0]  # For single file
            else:
                await message.reply("❌ Invalid file reference.")
                return

            # Fetch file info for display
            try:
                f_msg = await client.get_messages(channel_id, msg_id)
                if f_msg.document:
                    file_name = f_msg.document.file_name
                    file_size = f_msg.document.file_size
                    mime_type = f_msg.document.mime_type or "video/mp4"
                elif f_msg.video:
                    file_name = f_msg.video.file_name or "video.mp4"
                    file_size = f_msg.video.file_size
                    mime_type = f_msg.video.mime_type or "video/mp4"
                else:
                    file_name = "file"
                    file_size = 0
                    mime_type = "application/octet-stream"
            except Exception as e:
                await message.reply(f"❌ Error fetching file info: {e}")
                return

            # Generate streaming token
            token = await client.mongodb.create_stream_token(
                user_id=message.from_user.id,
                channel_id=channel_id,
                msg_id=msg_id,
                filename=file_name,
                expiry_hours=client.stream_token_expiry
            )

            # Build streaming URL
            stream_url = f"{client.stream_domain}/stream/{token}/{file_name}"

            # Build external player intents
            intents = {
                "vlc": f"intent:{stream_url}#Intent;action=android.intent.action.VIEW;type=video/*;package=org.videolan.vlc;end",
                "mx": f"intent:{stream_url}#Intent;action=android.intent.action.VIEW;type=video/*;package=com.mxtech.videoplayer.ad;end",
                "mx_pro": f"intent:{stream_url}#Intent;action=android.intent.action.VIEW;type=video/*;package=com.mxtech.videoplayer.pro;end",
                "playit": f"playit://playerv2/video?url={stream_url}",
                "km": f"intent:{stream_url}#Intent;action=android.intent.action.VIEW;type=video/*;package=com.kmplayer;end",
                "splayer": f"intent:{stream_url}#Intent;action=com.young.simple.player.playback_online;package=com.young.simple.player;end",
                "hd": f"intent:{stream_url}#Intent;action=android.intent.action.VIEW;type=video/*;package=uplayer.video.player;end",
            }

            # Auto-delete warning
            warning = ""
            if client.auto_del > 0:
                warning = f"\n\n⚠️ **File will be deleted in {humanize.naturaldelta(client.auto_del)} after download.**"

            # Create buttons
            buttons = [
                [InlineKeyboardButton("📥 Download", callback_data=f"download_{channel_id}_{msg_id}_{token}")],
                [
                    InlineKeyboardButton("🎬 VLC", url=intents["vlc"]),
                    InlineKeyboardButton("🎬 MX", url=intents["mx"]),
                ],
                [
                    InlineKeyboardButton("🌐 Web App", url=stream_url),
                    InlineKeyboardButton("ℹ️ More", callback_data=f"more_{token}"),
                ],
            ]

            # Send streaming menu
            await message.reply(
                f"**📂 {file_name}**\n"
                f"**📦 Size:** {humanize.naturalsize(file_size)}\n"
                f"**🔗 Type:** {mime_type.split('/')[0].capitalize()}\n"
                f"{warning}\n\n"
                f"👆 Choose an option:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return
        # ==================== END PREMIUM STREAMING MENU ====================

        ## If not premium and token verification enabled, show shortener
if not is_premium_user and token_verification_enabled:
    temp_msg = await message.reply(f"🔄 **{sc('generating your link')}...**")
    
    content_name = ""
    try:
        if original_base64.startswith("batch_"):
            b_id = original_base64.replace("batch_", "").strip()
            batch = await client.mongodb.get_batch(b_id)
            if batch:
                content_name = f"📦 <b>{batch.get('base_name', 'Batch Pack')}</b>\n\n"
        elif ids:
            try:
                t_msg_id = ids[0]
                main_db = getattr(client, 'db_channel_id', client.db)
                extra_dbs = await client.mongodb.get_db_channels()
                caption_channels = [custom_chat_id] if custom_chat_id else [main_db] + extra_dbs
                
                for chan in caption_channels:
                    try:
                        if not chan: continue
                        f_msg = await client.get_messages(chan, t_msg_id)
                        if f_msg and not f_msg.empty:
                            if f_msg.document:
                                content_name = f"🎬 <b>{f_msg.document.file_name}</b>\n\n"
                            break
                    except: continue
            except: pass
    except Exception as e:
        client.LOGGER(__name__, client.name).warning(f"Error fetching content name: {e}")
    
    access_token = secrets.token_hex(16)
    await client.mongodb.create_access_token(user_id, original_base64, access_token)
    
    file_link = f"https://t.me/{client.username}?start={original_base64}_{access_token}"
    shortened_url = await shorten_url(file_link)
    
    await temp_msg.delete()
    
    premium_text = (
        f"{content_name}"
        f"<b>🔗 {sc('your file link')}:</b>\n\n"
        f"<blockquote>👉 {sc('solve the shortener to unlock your file')}</blockquote>\n\n"
        f"<b>💎 {sc('want direct access')}?</b> {sc('buy premium')}!"
    )
    
    # FIX: Validate shortened_url and send safely
    try:
        # Ensure shortened_url is valid
        if not shortened_url or not shortened_url.startswith(('http://', 'https://')):
            shortened_url = file_link  # fallback to original
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"⌜{sc('ᴏᴘᴇɴ ʟɪɴᴋ')}⌟", url=shortened_url)],
            [
                InlineKeyboardButton(f"「{sc('ᴛᴜᴛᴏʀɪᴀʟ')}」", url="https://t.me/ProCineflix/45"),
                InlineKeyboardButton(f"「{sc('ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ')}」", url="https://t.me/ProCineflix/43")
            ]
        ])
        
        await client.send_photo(
            chat_id=message.chat.id,
            photo="https://files.catbox.moe/bktufd.jpg",
            caption=premium_text,
            reply_markup=buttons,
            protect_content=True
        )
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Send photo error: {e}")
        # Fallback: send simple text without buttons
        await message.reply(
            f"{content_name}"
            f"🔗 **Your link:**\n{file_link}\n\n"
            f"Solve the shortener to get your file."
        )
    
    if original_base64.startswith("batch_"):
        message.stop_propagation()
    return
        
        # Handle batch links after verification
        if original_base64.startswith("batch_"):
             batch_id = original_base64.replace("batch_", "").strip()
             from plugins.batch_handler import process_batch
             await process_batch(client, message, batch_id)
             message.stop_propagation()
             return

        # ------------------ FETCH AND SEND FILES (UPDATED FOR MULTI-DB) ------------------
        temp_msg = await message.reply(f"{sc('wait a sec')}..")
        
        # Get all possible DB channels to search
        main_db = getattr(client, 'db_channel_id', client.db)
        extra_dbs = await client.mongodb.get_db_channels()
        
        # If hybrid token provided a specific ID, try that first, then fall back to all DBs
        search_channels = [custom_chat_id] if custom_chat_id else [main_db] + extra_dbs
        
        valid_messages = []
        
        for channel in search_channels:
            if not channel: continue
            try:
                messages = await get_messages(client, ids, channel)
                # Filter out None/Empty messages
                valid_messages = [msg for msg in messages if msg and not getattr(msg, 'empty', True)]
                if valid_messages:
                    break # Found the file!
            except Exception:
                continue

        if not valid_messages:
            await temp_msg.edit_text(f"{sc('couldnt find the files in database')}.")
            return
            
        await temp_msg.delete()

        yugen_msgs = []
        for msg in valid_messages:
            caption = (
                client.messages.get('CAPTION', '').format(
                    previouscaption=f"<blockquote>{msg.caption.html}</blockquote>" if msg.caption else f"<blockquote>{msg.document.file_name}</blockquote>"
                )
                if client.messages.get('CAPTION', '') and msg.document
                else (msg.caption.html if msg.caption else "")
            )

            try:
                copied_msg = await msg.copy(
                    chat_id=user_id,
                    caption=caption,
                    protect_content=client.protect
                )
                yugen_msgs.append(copied_msg)
            except Exception as e:
                client.LOGGER(__name__, client.name).warning(f"Failed to copy message {msg.id}: {e}")

        if yugen_msgs and client.auto_del > 0:
            warning = await client.send_message(
                user_id,
                f"<b>⚠️ {sc('file will be deleted in')} {humanize.naturaldelta(client.auto_del)}.</b>"
            )
            asyncio.create_task(delete_files(yugen_msgs, client, warning, text))
        elif not yugen_msgs:
            await client.send_message(
                user_id,
                f"❌ {sc('failed to send files. please try again later.')}"
            )
        return

    # ---------------- NORMAL /start UI ----------------
    if user_id in client.admins:
        markup = home_buttons_admin()
    else:
        markup = home_buttons()
    
    photo = client.messages.get("START_PHOTO", "")
    if photo:
        await client.send_photo(
            chat_id=message.chat.id,
            photo=photo,
            caption=client.messages.get('START', 'No Start Msg').format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=f"@{message.from_user.username}" if message.from_user.username else None,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=markup
        )
    else:
        await client.send_message(
            chat_id=message.chat.id,
            text=client.messages.get('START', 'No Start Message').format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=f"@{message.from_user.username}" if message.from_user.username else None,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=markup
        )
