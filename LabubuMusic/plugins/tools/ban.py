from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import ChatAdminRequired, UserNotParticipant

from LabubuMusic import matto_bot
from LabubuMusic.utils.permissions import adminsOnly
from LabubuMusic.utils.functions import extract_user_and_reason

@matto_bot.on_message(filters.command(["ban", "dban"]) & filters.group)
@adminsOnly("can_restrict_members")
async def ban_member_handler(client, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    
    if not user_id:
        return await message.reply_text("I can't find that user.")
        
    try:
        member_info = await message.chat.get_member(user_id)
        if member_info.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("I cannot ban an admin.")
    except:
        pass

    try:
        await message.chat.ban_member(user_id)
        reply_text = f"🚫 **Banned:** {user_id}"
        if reason:
            reply_text += f"\n📝 **Reason:** {reason}"
            
        await message.reply_text(reply_text)
    except ChatAdminRequired:
        await message.reply_text("I don't have permission to ban users.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@matto_bot.on_message(filters.command("unban") & filters.group)
@adminsOnly("can_restrict_members")
async def unban_member_handler(client, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    
    if not user_id:
        return await message.reply_text("Specify a user to unban.")
        
    try:
        await message.chat.unban_member(user_id)
        
        btn = InlineKeyboardMarkup([[
            InlineKeyboardButton("Join Chat", url=f"https://t.me/{message.chat.username}")
        ]]) if message.chat.username else None
        
        await message.reply_text(
            f"✅ **Unbanned:** {user_id}",
            reply_markup=btn
        )
    except Exception as e:
        await message.reply_text(f"Failed to unban: {e}")