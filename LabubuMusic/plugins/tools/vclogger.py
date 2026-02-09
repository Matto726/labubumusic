import random
import asyncio
from pyrogram import filters
from LabubuMusic import matto_bot
from LabubuMusic.utils.database import get_assistant

VC_MESSAGES = [
    "👋 {0} left the voice chat. Come back soon!",
    "🔇 {0} disconnected.",
    "🏃 {0} ran away from the VC!"
]

async def log_vc_exit(user_id, chat_id):
    try:
        user = await matto_bot.get_users(user_id)
        name = f"<b>{user.first_name}</b>"
        text = random.choice(VC_MESSAGES).format(name)
        
        msg = await matto_bot.send_message(chat_id, text)
        await asyncio.sleep(10)
        await msg.delete()
    except:
        pass
    