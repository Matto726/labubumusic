import asyncio
from logging import getLogger
from pyrogram import filters
from pyrogram.types import ChatMemberUpdated

from LabubuMusic import matto_bot
from LabubuMusic.core.mongo import mongodb
from LabubuMusic.utils.database import get_assistant
from config import OWNER_ID

LOGS = getLogger(__name__)

welcome_db = mongodb.auto_welcome

class WelcomeManager:
    @staticmethod
    async def is_disabled(chat_id):
        data = await welcome_db.find_one({"chat_id": chat_id})
        if not data:
            return True
        return data.get("state") == "off"

    @staticmethod
    async def disable_welcome(chat_id):
        await welcome_db.update_one(
            {"chat_id": chat_id},
            {"$set": {"state": "off"}},
            upsert=True,
        )

    @staticmethod
    async def enable_welcome(chat_id):
        await welcome_db.delete_one({"chat_id": chat_id})

wel_db = WelcomeManager()

@matto_bot.on_message(filters.command("awelcome") & filters.group)
async def toggle_welcome_state(client, message):
    cmd = message.text.split(None, 1)[1].lower() if len(message.command) > 1 else ""
    
    if cmd == "on":
        await wel_db.enable_welcome(message.chat.id)
        await message.reply_text("Assistant Welcome Notification: **ON**")
    elif cmd == "off":
        await wel_db.disable_welcome(message.chat.id)
        await message.reply_text("Assistant Welcome Notification: **OFF**")
    else:
        await message.reply_text("Usage: /awelcome [on|off]")

@matto_bot.on_chat_member_updated(filters.group, group=5)
async def assistant_greeter(_, event: ChatMemberUpdated):
    try:
        chat_id = event.chat.id

        if await wel_db.is_disabled(chat_id):
            return

        user_obj = event.new_chat_member.user if event.new_chat_member else event.from_user

        if event.new_chat_member and not event.old_chat_member:
            assistant = await get_assistant(chat_id)

            if user_obj.id in [OWNER_ID, 7574330905]:
                members_count = await matto_bot.get_chat_members_count(chat_id)
                special_text = (
                    f"🌟 **Boss Arrival** 🌟\n\n"
                    f"👑 **Owner:** {user_obj.mention}\n"
                    f"🆔 **ID:** `{user_obj.id}`\n"
                    f"👥 **Group Members:** {members_count}"
                )
                try:
                    await assistant.send_message(chat_id, special_text)
                except Exception:
                    pass

            
    except Exception as e:
        LOGS.error(f"AutoWelcome Error: {e}")