from pyrogram import filters, Client
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import ChatAdminRequired, UserNotParticipant
from pyrogram.types import (
    CallbackQuery, InlineKeyboardButton, 
    InlineKeyboardMarkup, Message
)
from LabubuMusic import matto_bot
from LabubuMusic.core.mongo import mongodb
from LabubuMusic.misc import SUDO_USERS
from config import MONGO_DB_URI

fsub_db = mongodb.force_subscription_status

@matto_bot.on_message(filters.command(["fsub", "forcesub"]) & filters.group)
async def configure_forcesub(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    member = await client.get_chat_member(chat_id, user_id)
    if not (member.privileges and member.privileges.can_restrict_members) and user_id not in SUDO_USERS:
        return await message.reply_text("You need 'Restrict Members' permission to manage Force Subscription.")

    if len(message.command) != 2:
        return await message.reply_text("Usage: /fsub [Channel Username | off]")

    arg = message.command[1].lower()

    if arg in ["off", "disable"]:
        await fsub_db.delete_one({"chat_id": chat_id})
        return await message.reply_text("❌ Force Subscription has been **disabled** for this group.")

    try:
        channel = await client.get_chat(arg)
        if not channel.username:
            return await message.reply_text("The channel must have a username.")
            
        bot_member = await channel.get_member(client.me.id)
        if not bot_member.privileges:
            return await message.reply_text("I need to be an **Admin** in that channel first.")

        await fsub_db.update_one(
            {"chat_id": chat_id},
            {"$set": {"channel": channel.id, "username": channel.username}},
            upsert=True
        )
        await message.reply_text(f"✅ Force Subscription enabled! Linked to **@{channel.username}**.")

    except Exception as e:
        await message.reply_text(f"Error: Could not access channel. Make sure I am an admin there.\nException: {e}")

@matto_bot.on_message(filters.group, group=30)
async def enforce_subscription_check(client: Client, message: Message):
    if not message.from_user or message.from_user.is_bot:
        return

    chat_id = message.chat.id
    data = await fsub_db.find_one({"chat_id": chat_id})
    
    if not data:
        return

    channel_username = data.get("username")
    channel_id = data.get("channel")

    try:
        await client.get_chat_member(channel_id, message.from_user.id)
    except UserNotParticipant:
        channel_url = f"https://t.me/{channel_username}"
        try:
            await message.delete()
        except:
            pass

        btn = InlineKeyboardMarkup([[
            InlineKeyboardButton("๏ Join Channel ๏", url=channel_url)
        ]])
        
        warning_msg = await message.reply_photo(
            photo="https://envs.sh/Tn_.jpg",
            caption=(
                f"👋 **Hello {message.from_user.mention},**\n\n"
                f"You must join [This Channel]({channel_url}) to send messages here."
            ),
            reply_markup=btn
        )
    except ChatAdminRequired:
        await fsub_db.delete_one({"chat_id": chat_id})
        await message.reply_text("🚫 **Force Subscription Disabled:** I am no longer an admin in the target channel.")