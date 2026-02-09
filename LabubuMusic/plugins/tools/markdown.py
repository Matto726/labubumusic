from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from LabubuMusic import matto_bot
from LabubuMusic.utils.functions import MARKDOWN

@matto_bot.on_message(filters.command("markdownhelp"))
async def markdown_guide(client, message: Message):
    btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("View Syntax", url=f"http://t.me/{matto_bot.username}?start=mkdwn_help")
    ]])
    
    if message.chat.type != ChatType.PRIVATE:
        await message.reply_text(
            "Click the button below to see available Markdown formatting.",
            reply_markup=btn
        )
    else:
        await message.reply_text(
            MARKDOWN,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )