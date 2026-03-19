# Made by @Awakeners_Bots
# GitHub: https://github.com/Awakener_Bots

from pyrogram import Client, filters, enums
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import MSG_EFFECT
from helper.font_converter import to_small_caps as sc

# ==================== CONFIGURABLE LINKS ====================
CHANNEL_MAIN = "https://t.me/YourMainChannel"          # Replace with your main channel URL
CHANNEL_MOVIES = "http://t.me/Cineflix_Saga"
CHANNEL_SERIES = "http://t.me/seriesflix_Saga"
CHANNEL_ANIMES = "http://t.me/anime_Saga"              # ANIMES button
CHANNEL_ADULT = "http://t.me/culturedxsaga"            # ADULT button – replace with actual link
# ============================================================

# Credit info text with HTML links – bold small caps

CREDIT_INFO = """
<b>⍟───[ ᴍʏ ᴄʀᴇᴅɪᴛꜱ & ɪɴꜰᴏ ]───⍟

➥ ᴏᴡɴᴇʀ : <a href='t.me/Xeonflixadmin'>xᴇᴏɴ</a>
➥ ʙᴀꜱᴇ ᴄᴏᴅᴇ : <a href='t.me/cosmic_freak'>ʏᴀᴛᴏ</a>
➥ ᴇxᴛʀᴀ ᴄᴏᴅᴇ : <a href='t.me/MrXeonTG'>ɢᴏᴊᴏ ꜱᴀᴛᴏʀᴜ</a>
➥ ᴛʜᴀɴᴋꜱ ᴛᴏ : <a href='t.me/codexbotz'>ᴄᴏᴅᴇx ʙᴏᴛ</a>
➥ ᴛʜᴀɴᴋꜱ ᴛᴏ : <a href='tg://settings'>ᴛʜɪs ᴘᴇʀsᴏɴ</a>
➥ ꜱᴏᴜʀᴄᴇ ᴄᴏᴅᴇ : <a href="https://youtu.be/xvFZjo5PgG0?si=xED3mG2R8_msmL2u">ʜᴇʀᴇ</a>
➥ ᴛʜɪꜱ ɪꜱ ᴀ ᴘʀɪᴠᴀᴛᴇ sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ ᴘʀᴏᴊᴇᴄᴛ</b>"""

# Disclaimer text – exact copy with small caps, wrapped in bold
DISCLAIMER_TEXT = """
<b>ᴀʟʟ ᴛʜᴇ ᴄᴏɴᴛᴇɴᴛꜱ ɪɴ ᴛʜɪꜱ ʙᴏᴛ ᴀʀᴇ ᴄʀᴇᴀᴛᴇᴅ ʙʏ ᴛʜᴇ ɪɴᴛᴇʀɴᴇᴛ ᴏʀ ᴘᴏꜱᴛᴇᴅ ʙʏ ᴄᴏᴘʏʀɪɢʜᴛ ᴄᴏᴍᴘᴀɴɪᴇꜱ. ᴛʜᴇꜱᴇ ᴄɪɴᴇᴍᴀ ᴏʀ ꜰɪʟᴍꜱ ᴀʀᴇ ᴏɴʟɪɴᴇ ᴇꜱᴛɪᴍᴀᴛᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ɪɴᴛᴇʀɴᴇᴛ. ɪ ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴀɴʏ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴏɴ ᴛʜɪꜱ ꜰɪʟᴇꜱ ᴀɴᴅ ᴛʜᴇꜱᴇ ꜰɪʟᴇꜱ ᴀʀᴇ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴛʜᴇ ᴜꜱᴇʀꜱ. ɪꜰ ʏᴏᴜ ᴛʜɪɴᴋ ᴛʜɪꜱ ʙᴏᴛ ɪꜱ ʜᴀʀᴍꜰᴜʟ ᴛᴏ ʏᴏᴜʀ ɪɴᴛᴇʀɴᴇᴛ ᴘʀᴏᴘᴇʀᴛʏ, ᴄᴏɴᴛᴀᴄᴛ ᴛʜᴇ ʀᴇꜱᴘᴇᴄᴛɪᴠᴇ ᴏꜰꜰɪᴄɪᴀʟ ᴀᴜᴛʜᴏʀɪᴛɪᴇꜱ ᴛᴏ ɢᴇᴛ ʀᴇᴍᴏᴠᴇᴅ. ɪᴛ ɪꜱ ʏᴏᴜʀ ʀᴇꜱᴘᴏɴꜱɪʙɪʟɪᴛʏ ᴛᴏ ᴄᴏᴍᴘʟʏ ᴡɪᴛʜ ᴀʟʟ ᴀᴘᴘʟɪᴄᴀʙʟᴇ ʟᴀᴡꜱ ɪɴ ʏᴏᴜʀ ᴄᴏᴜɴᴛʀʏ ʙᴇꜰᴏʀᴇ ᴜꜱɪɴɢ ᴛʜɪꜱ ʙᴏᴛ.</b>
"""

# ==================== NEW PREMIUM PLANS TEXT ====================
PREPLANSS_TXT = """<b>👋 ʜᴇʏ {first}

ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇ ʙᴇɴɪꜰɪᴛꜱ 🎁
❏ ɴᴏ ʟɪɴᴋ ꜱʜᴏʀᴛᴇɴᴇʀ
❏ ɢᴇᴛ ᴅɪʀᴇᴄᴛ ғɪʟᴇs
❏ ᴀᴅ-ғʀᴇᴇ ᴇxᴘᴇʀɪᴇɴᴄᴇ
❏ ʙᴇꜱᴛ ᴠᴀʟᴜᴇ ꜰᴏʀ ᴍᴏɴᴇʏ
❏ ᴘʀɪᴏʀɪᴛʏ ᴄᴏɴᴛᴇɴᴛ
❏ ᴇxᴄʟᴜꜱɪᴠᴇ ᴅɪꜱᴄᴏᴜɴᴛꜱ

ᴄʜᴇᴄᴋᴏᴜᴛ ᴘʟᴀɴs ᴘʀɪᴄᴇs: <a href="https://t.me/ProCineflix/43">›› ᴄʟɪᴄᴋ ʜᴇʀᴇ</a></b>"""
# ============================================================

# ==================== BUTTON LAYOUT FUNCTIONS ====================

def home_buttons():
    """Home page buttons (normal user) – no Next button"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("• ᴅɪꜱᴄʟᴀɪᴍᴇʀ •", callback_data="disclaimer"),
         InlineKeyboardButton("• ᴀʙᴏᴜᴛ •", callback_data="about")],
        [InlineKeyboardButton("• ᴘʀᴇᴍɪᴜᴍ •", callback_data="premium_plans"),
         InlineKeyboardButton("• ᴄʜᴀɴɴᴇʟ •", url=CHANNEL_MAIN)]
    ])

def home_buttons_admin():
    """Home page with Settings button for admins – no Next button"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("• ꜱᴇᴛᴛɪɴɢꜱ •", callback_data="settings")],
        [InlineKeyboardButton("• ᴅɪꜱᴄʟᴀɪᴍᴇʀ •", callback_data="disclaimer"),
         InlineKeyboardButton("• ᴀʙᴏᴜᴛ •", callback_data="about")],
        [InlineKeyboardButton("• ᴘʀᴇᴍɪᴜᴍ •", callback_data="premium_plans"),
         InlineKeyboardButton("• ᴄʜᴀɴɴᴇʟ •", url=CHANNEL_MAIN)]
    ])

def about_submenu_buttons():
    """Buttons shown inside About – Channels, Credit, Settings, Back"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("• ᴄʜᴀɴɴᴇʟꜱ •", callback_data="channels_menu"),
         InlineKeyboardButton("• ᴄʀᴇᴅɪᴛꜱ •", callback_data="credit_info")],
        [InlineKeyboardButton("• ꜱᴇᴛᴛɪɴɢꜱ •", callback_data="settings"),
         InlineKeyboardButton("• ʙᴀᴄᴋ •", callback_data="home")]
    ])

def channels_menu_buttons():
    """Channels submenu – 3 rows of 2 buttons each (as requested)"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("• ᴍᴏᴠɪᴇꜱ •", url=CHANNEL_MOVIES),
         InlineKeyboardButton("• ꜱᴇʀɪᴇꜱ •", url=CHANNEL_SERIES)],
        [InlineKeyboardButton("• ᴀɴɪᴍᴇꜱ •", url=CHANNEL_ANIMES),
         InlineKeyboardButton("• ᴀᴅᴜʟᴛ •", url=CHANNEL_ADULT)],
        [InlineKeyboardButton("• ʜᴏᴍᴇ •", callback_data="home"),
         InlineKeyboardButton("• ᴄʟᴏꜱᴇ •", callback_data="close")]
    ])

# ==================== CALLBACK HANDLERS ====================

@Client.on_callback_query(filters.regex('^home$'))
async def home_callback(client: Client, query: CallbackQuery):
    """Home page – with admin check"""
    user_id = query.from_user.id
    if user_id in client.admins:
        markup = home_buttons_admin()
    else:
        markup = home_buttons()
    await query.message.edit_text(
        text=client.messages.get('START', 'Welcome!').format(
            first=query.from_user.first_name,
            mention=query.from_user.mention
        ),
        reply_markup=markup,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex('^about$'))
async def about_callback(client: Client, query: CallbackQuery):
    """About page – now shows Channels, Credit, and Settings submenu (no extra text)"""
    about_text = client.messages.get('ABOUT', 'About this bot').format(
        owner_id=client.owner,
        bot_username=client.username,
        first=query.from_user.first_name,
        last=query.from_user.last_name,
        username=None if not query.from_user.username else '@' + query.from_user.username,
        mention=query.from_user.mention,
        id=query.from_user.id
    )
    await query.message.edit_text(
        text=about_text,  # Removed the extra line
        reply_markup=about_submenu_buttons(),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex('^channels_menu$'))
async def channels_menu_callback(client: Client, query: CallbackQuery):
    """Channels submenu – Updated with text to prevent API error"""
    await query.message.edit_text(
        text="<b>ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟs:</b>",  # Text cannot be empty
        reply_markup=channels_menu_buttons(),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex('^credit_info$'))
async def credit_info_callback(client: Client, query: CallbackQuery):
    """Credit info panel with HTML links – bold small caps"""
    await query.message.edit_text(
        text=CREDIT_INFO,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Home", callback_data="home"),
             InlineKeyboardButton("Close", callback_data="close")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex('^disclaimer$'))
async def disclaimer_callback(client: Client, query: CallbackQuery):
    """Disclaimer panel – bold small caps"""
    await query.message.edit_text(
        text=DISCLAIMER_TEXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Back", callback_data="home")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex('^close$'))
async def close_callback(client: Client, query: CallbackQuery):
    """Delete the message"""
    await query.message.delete()

# -------------------- Premium plans callback (updated) --------------------

@Client.on_callback_query(filters.regex('^premium_plans$'))
async def premium_plans_callback(client: Client, query: CallbackQuery):
    premium_text = PREPLANSS_TXT.format(first=query.from_user.first_name)
    
    buttons = [
        [InlineKeyboardButton("💰 Buy Now", url="https://t.me/mfxdmbot")],
        [InlineKeyboardButton("🔙 Back", callback_data="home")]
    ]
    
    await query.message.edit_text(
        text=premium_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )
    return

# -------------------- Ban/Unban commands (keep) --------------------

@Client.on_message(filters.command('ban'))
async def ban(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    try:
        user_ids = message.text.split(maxsplit=1)[1]
        c = 0
        for user_id in user_ids.split():
            user_id = int(user_id)
            c += 1
            if user_id in client.admins:
                continue
            if not await client.mongodb.present_user(user_id):
                await client.mongodb.add_user(user_id, True)
                continue
            else:
                await client.mongodb.ban_user(user_id)
        return await message.reply(f"__{c} users have been banned!__")
    except Exception as e:
        return await message.reply(f"**Error:** `{e}`")

@Client.on_message(filters.command('unban'))
async def unban(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    try:
        user_ids = message.text.split(maxsplit=1)[1]
        c = 0
        for user_id in user_ids.split():
            user_id = int(user_id)
            c += 1
            if user_id in client.admins:
                continue
            if not await client.mongodb.present_user(user_id):
                await client.mongodb.add_user(user_id)
                continue
            else:
                await client.mongodb.unban_user(user_id)
        return await message.reply(f"__{c} users have been unbanned!__")
    except Exception as e:
        return await message.reply(f"**Error:** `{e}`")

@Client.on_callback_query(filters.regex(r"^download_"))
async def download_callback(client: Client, query: CallbackQuery):
    _, channel_id, msg_id, token = query.data.split("_")
    channel_id = int(channel_id)
    msg_id = int(msg_id)
    user_id = query.from_user.id

    token_data = await client.mongodb.validate_stream_token(token)
    if not token_data or token_data['user_id'] != user_id:
        await query.answer("❌ Invalid or expired link. Please generate a new one.", show_alert=True)
        return

    credit_system_enabled = await client.mongodb.is_credit_system_enabled()
    is_premium = await client.mongodb.is_premium(user_id)

    if credit_system_enabled and not is_premium:
        from helper.enhanced_credit_db import EnhancedCreditDB
        enhanced_db = EnhancedCreditDB(client.db_uri, client.db_name)
        credit_data = await enhanced_db.get_credits(user_id)
        if credit_data.get("balance", 0) <= 0:
            await query.answer("❌ You don't have enough credits.", show_alert=True)
            return
        await enhanced_db.use_credit(user_id)
        remaining = credit_data["balance"] - 1
        await query.message.reply(f"⚡ 1 credit used. Remaining: {remaining}")

    await query.answer("Sending file...")
    
    from helper.helper_func import get_messages, delete_files
    messages = await get_messages(client, [msg_id], channel_id)
    if not messages:
        await query.message.reply("❌ File not found.")
        return

    sent_msgs = []
    for msg in messages:
        caption = (
            client.messages.get('CAPTION', '').format(
                previouscaption=f"<blockquote>{msg.caption.html}</blockquote>" if msg.caption else f"<blockquote>{msg.document.file_name}</blockquote>"
            )
            if client.messages.get('CAPTION', '') and msg.document
            else (msg.caption.html if msg.caption else "")
        )
        try:
            copied = await msg.copy(
                chat_id=user_id,
                caption=caption,
                protect_content=client.protect
            )
            sent_msgs.append(copied)
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Failed to copy: {e}")

    if sent_msgs and client.auto_del > 0:
        warning = await client.send_message(
            user_id,
            f"<b>⚠️ File will be deleted in {humanize.naturaldelta(client.auto_del)}.</b>"
        )
        asyncio.create_task(delete_files(sent_msgs, client, warning, ""))

    await query.message.edit_reply_markup(None)

@Client.on_callback_query(filters.regex(r"^more_"))
async def more_players_callback(client: Client, query: CallbackQuery):
    token = query.data.split("_")[1]
    token_data = await client.mongodb.validate_stream_token(token)
    if not token_data:
        await query.answer("❌ Token expired", show_alert=True)
        return

    stream_url = f"{client.stream_domain}/stream/{token}/{token_data.get('filename', 'video.mp4')}"
    
    intents = {
        "vlc": f"intent:{stream_url}#Intent;action=android.intent.action.VIEW;type=video/*;package=org.videolan.vlc;end",
        "mx": f"intent:{stream_url}#Intent;action=android.intent.action.VIEW;type=video/*;package=com.mxtech.videoplayer.ad;end",
        "mx_pro": f"intent:{stream_url}#Intent;action=android.intent.action.VIEW;type=video/*;package=com.mxtech.videoplayer.pro;end",
        "playit": f"playit://playerv2/video?url={stream_url}",
        "km": f"intent:{stream_url}#Intent;action=android.intent.action.VIEW;type=video/*;package=com.kmplayer;end",
        "splayer": f"intent:{stream_url}#Intent;action=com.young.simple.player.playback_online;package=com.young.simple.player;end",
        "hd": f"intent:{stream_url}#Intent;action=android.intent.action.VIEW;type=video/*;package=uplayer.video.player;end",
    }

    text = "**🎬 External Players**\n\n"
    text += f"• [VLC]({intents['vlc']})\n"
    text += f"• [MX Player]({intents['mx']})\n"
    text += f"• [MX Player Pro]({intents['mx_pro']})\n"
    text += f"• [PLAYit]({intents['playit']})\n"
    text += f"• [KMPlayer]({intents['km']})\n"
    text += f"• [S Player]({intents['splayer']})\n"
    text += f"• [HD Player]({intents['hd']})\n"
    
    await query.message.reply(text, disable_web_page_preview=True)
    await query.answer()
