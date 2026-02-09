import random
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from config import LOG_GROUP_ID
from LabubuMusic import matto_bot
from LabubuMusic.utils.database import add_served_chat, get_assistant, delete_served_chat

WELCOME_IMG = "https://files.catbox.moe/ajobub.jpg"
LEAVE_IMGS = [
    "https://telegra.ph/file/1949480f01355b4e87d26.jpg",
    "https://telegra.ph/file/3ef2cc0ad2bc548bafb30.jpg",
    "https://telegra.ph/file/a7d663cd2de689b811729.jpg",
    "https://telegra.ph/file/6f19dc23847f5b005e922.jpg",
    "https://telegra.ph/file/2973150dd62fd27a3a6ba.jpg",
]

@matto_bot.on_message(filters.new_chat_members, group=-10)
async def new_group_watcher(client, message: Message):
    try:
        assistant_client = await get_assistant(message.chat.id)
        chat_obj = message.chat
        
        for new_mem in message.new_chat_members:
            if new_mem.id == matto_bot.id:
                
                total_members = await matto_bot.get_chat_members_count(chat_obj.id)
                chat_user = message.chat.username or "Private Group"

                invite_url = ""
                try:
                    if not message.chat.username:
                        link = await matto_bot.export_chat_invite_link(message.chat.id)
                        invite_url = f"\nGroup Link: {link}" if link else ""
                except Exception:
                    pass
                
                log_text = (
                    f"🎵 **New Group Added**\n\n"
                    f"**Chat:** {message.chat.title}\n"
                    f"**ID:** `{message.chat.id}`\n"
                    f"**Username:** @{chat_user}\n"
                    f"**Members:** {total_members}\n"
                    f"**Added By:** {message.from_user.mention}"
                    f"{invite_url}"
                )
                
                btn = None
                if message.from_user.id:
                    btn = InlineKeyboardMarkup([[
                        InlineKeyboardButton("👤 Added By", url=f"tg://openmessage?user_id={message.from_user.id}")
                    ]])
                
                await matto_bot.send_photo(
                    LOG_GROUP_ID,
                    photo=WELCOME_IMG,
                    caption=log_text,
                    reply_markup=btn
                )
                
                await add_served_chat(message.chat.id)
                if chat_user != "Private Group":
                    try:
                        await assistant_client.join_chat(chat_user)
                    except:
                        pass

    except Exception as ex:
        pass

@matto_bot.on_message(filters.left_chat_member, group=-12)
async def group_leave_watcher(client, message: Message):
    try:
        assistant_client = await get_assistant(message.chat.id)
        left_user = message.left_chat_member
        
        if left_user and left_user.id == (await matto_bot.get_me()).id:
            remover = message.from_user.mention if message.from_user else "Unknown"
            chat_title = message.chat.title
            
            log_msg = (
                f"✫ <b><u>#Left_Group</u></b> ✫\n\n"
                f"**Chat:** {chat_title}\n"
                f"**ID:** `{message.chat.id}`\n"
                f"**Removed By:** {remover}\n"
                f"**Bot:** @{matto_bot.username}"
            )
            
            await matto_bot.send_photo(
                LOG_GROUP_ID, 
                photo=random.choice(LEAVE_IMGS), 
                caption=log_msg
            )
            
            await delete_served_chat(message.chat.id)
            try:
                await assistant_client.leave_chat(message.chat.id)
            except:
                pass
    except Exception:
        pass