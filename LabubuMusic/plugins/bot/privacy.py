from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ParseMode
from LabubuMusic import matto_bot
import config

POLICY_TEXT = f"""
🔒 **Privacy Policy for {matto_bot.mention} !**

Your privacy is important to us.

@matto_bot.on_message(filters.command("privacy"))
async def privacy_policy_handler(client, message: Message):
    btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("View Privacy Policy", url=config.SUPPORT_GROUP)
    ]])
    
    await message.reply_text(
        POLICY_TEXT, 
        reply_markup=btn, 
        parse_mode=ParseMode.MARKDOWN, 
        disable_web_page_preview=True
    )