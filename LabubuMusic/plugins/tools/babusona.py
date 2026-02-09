import random
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from LabubuMusic import matto_bot

ROAST_LIST = [
    "You look like a before picture.",
    "I'd agree with you but then we'd both be wrong.",
    "You bring everyone so much joy when you leave the room.",
    "I'd explain it to you but I can't understand it for you.",
    "Don't be ashamed of who you are. That's your parents' job.",
    "Your secrets are always safe with me. I never even listen when you tell me them.",
]

@matto_bot.on_message(filters.command(["gali", "roast"]))
async def roast_command_handler(client, message: Message):
    chat_type = message.chat.type

    if chat_type == chat_type.PRIVATE:
        await message.reply_text(random.choice(ROAST_LIST))
        return

    user_status = await message.chat.get_member(message.from_user.id)
    allowed_roles = ["administrator", "creator"]
    
    if user_status.status.value in allowed_roles:
        target = message.reply_to_message
        text_payload = random.choice(ROAST_LIST)
        
        if target:
            sent_msg = await message.reply_text(f"{target.from_user.mention} {text_payload}")
        else:
            sent_msg = await message.reply_text(text_payload)

        await asyncio.sleep(60)
        try:
            await sent_msg.delete()
            await message.delete()
        except:
            pass
    else:
        warning_msg = await message.reply_text(
            "**🚫 Admin Only Command!**\n\n"
            "Use this in private chat if you want to test it."
        )
        await asyncio.sleep(5)
        try:
            await warning_msg.delete()
        except:
            pass