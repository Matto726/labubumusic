import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from LabubuMusic import matto_bot
from LabubuMusic.utils.permissions import adminsOnly

cleaning_queue = []

@matto_bot.on_message(filters.command(["zombies", "clean", "kickdeleted"]))
@adminsOnly("can_restrict_members")
async def purge_zombies(client, message: Message):
    chat_id = message.chat.id
    
    if chat_id in cleaning_queue:
        return await message.reply_text("⚠️ A cleaning process is already running in this chat.")
    
    cleaning_queue.append(chat_id)

    try:
        bot_member = await client.get_chat_member(chat_id, "me")
        if bot_member.status != ChatMemberStatus.ADMINISTRATOR:
            cleaning_queue.remove(chat_id)
            return await message.reply_text("❌ I need to be an **Admin** to do this.")
    except Exception as e:
        cleaning_queue.remove(chat_id)
        return await message.reply_text(f"Error checking permissions: {e}")

    status_msg = await message.reply_text("🔍 <b>Scanning for deleted accounts...</b>")
    deleted_accounts = []
    
    try:
        async for member in client.get_chat_members(chat_id):
            if member.user.is_deleted:
                deleted_accounts.append(member.user.id)
        
        count = len(deleted_accounts)
        
        if count > 0:
            await status_msg.edit_text(f"⚠️ Found **{count}** deleted accounts.\n🗑️ Cleaning initiated...")
            
            cleaned = 0
            for user_id in deleted_accounts:
                try:
                    await client.ban_chat_member(chat_id, user_id)
                    cleaned += 1
                    await asyncio.sleep(1)
                except FloodWait as f:
                    await asyncio.sleep(f.value)
                except Exception:
                    pass
            
            await status_msg.edit_text(f"✅ <b>Cleanup Complete!</b>\nRemoved {cleaned} deleted accounts.")
        else:
            await status_msg.edit_text("✅ <b>No deleted accounts found in this group.</b>")
            
    except Exception as e:
        await status_msg.edit_text(f"❌ An error occurred: {e}")
        
    finally:
        if chat_id in cleaning_queue:
            cleaning_queue.remove(chat_id)