import asyncio
import random
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from LabubuMusic import matto_bot

TAG_PROCESSES = []

TAG_EMOJIS = [
    "🌈", "🌟", "✨", "💫", "🔥", "💥", "🍄", "🌺", 
    "🍀", "🍁", "🦄", "🐼", "🐶", "🐱", "🐰", "🦊"
]

@matto_bot.on_message(filters.command(["tagall", "all", "mentionall"]) & filters.group)
async def tag_all_users(client, message):
    chat_id = message.chat.id
    
    if chat_id in TAG_PROCESSES:
        return await message.reply_text("A tagging process is already running here.")

    member = await client.get_chat_member(chat_id, message.from_user.id)
    if not (member.privileges and member.privileges.can_manage_chat):
        return await message.reply_text("Admins only!")

    msg_text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
    if not msg_text and message.reply_to_message:
        msg_text = message.reply_to_message.text

    if not msg_text:
        return await message.reply_text("Give me text or reply to a message.")

    TAG_PROCESSES.append(chat_id)
    await message.reply_text("Starting mass mention...")
    
    users_list = []
    async for m in client.get_chat_members(chat_id):
        if not m.user.is_bot and not m.user.is_deleted:
            users_list.append(m.user)
            
    try:
        for i in range(0, len(users_list), 5):
            if chat_id not in TAG_PROCESSES:
                break
                
            batch = users_list[i:i+5]
            tag_string = ""
            for user in batch:
                tag_string += f"[{random.choice(TAG_EMOJIS)}]({user.mention}) "
            
            final_msg = f"{msg_text}\n{tag_string}"
            
            if message.reply_to_message:
                await message.reply_to_message.reply_text(final_msg)
            else:
                await client.send_message(chat_id, final_msg)
                
            await asyncio.sleep(3)
    except Exception as e:
        await message.reply_text(f"Error: {e}")
    finally:
        if chat_id in TAG_PROCESSES:
            TAG_PROCESSES.remove(chat_id)

@matto_bot.on_message(filters.command(["stopmention", "cancel", "offmention"]) & filters.group)
async def stop_tagging(client, message):
    if message.chat.id in TAG_PROCESSES:
        TAG_PROCESSES.remove(message.chat.id)
        await message.reply_text("Stopped tagging process.")
    else:
        await message.reply_text("No active tagging process found.")