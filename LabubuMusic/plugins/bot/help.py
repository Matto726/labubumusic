from typing import Union
from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup

from LabubuMusic import matto_bot
from LabubuMusic.utils.database import get_lang
from LabubuMusic.utils.decorators.language import LanguageStart, languageCB
from LabubuMusic.utils.inline.help import (
    help_back_markup,
    private_help_panel,
    help_pannel_page1
)
from config import BANNED_USERS, START_IMG_URL, SUPPORT_GROUP
from strings import get_string, helpers

@matto_bot.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@matto_bot.on_callback_query(filters.regex("help_page_1") & ~BANNED_USERS)
async def help_menu_private(client, update: Union[types.Message, types.CallbackQuery]):
    is_cb = isinstance(update, types.CallbackQuery)
    
    if is_cb:
        try:
            await update.answer()
        except:
            pass
        chat_id = update.message.chat.id
    else:
        chat_id = update.chat.id

    lang_code = await get_lang(chat_id)
    txt = get_string(lang_code)
    
    markup = help_pannel_page1(txt, True) if is_cb else help_pannel_page1(txt)
    caption_txt = txt["help_1"].format(SUPPORT_GROUP)

    if is_cb:
        await update.edit_message_text(caption_txt, reply_markup=markup)
    else:
        try:
            await update.delete()
        except:
            pass
        await update.reply_photo(
            photo=START_IMG_URL,
            caption=caption_txt,
            reply_markup=markup,
        )

@matto_bot.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_menu_group(client, message, _):
    keyboard = private_help_panel(_)
    await message.reply_text(_["help_2"], reply_markup=InlineKeyboardMarkup(keyboard))

@matto_bot.on_callback_query(filters.regex("help_callback") & ~BANNED_USERS)
@languageCB
async def help_details_cb(client, cb, _):
    raw_data = cb.data.strip()
    key = raw_data.split(None, 1)[1]

    page_map = {
        1: ["hb1", "hb2", "hb3", "hb4", "hb5", "hb6", "hb7", "hb8", "hb9", "hb10"],
        2: ["hb11", "hb12", "hb13", "hb14", "hb15", "hb17", "hb18", "hb19", "hb20", "hb21"],
        3: ["hb22", "hb23", "hb24", "hb25", "hb26", "hb27", "hb28", "hb29", "hb30", "hb31"],
        4: ["hb32", "hb33", "hb34", "hb35", "hb36", "hb37", "hb38", "hb39"]
    }

    target_page = 1
    for page_num, keys in page_map.items():
        if key in keys:
            target_page = page_num
            break

    back_btn = help_back_markup(_, page=target_page)

    help_attr_name = f"HELP_{key.replace('hb', '')}"
    
    try:
        help_text = getattr(helpers, help_attr_name)
        await cb.edit_message_text(help_text, reply_markup=back_btn)
    except AttributeError:
        await cb.edit_message_text("Help section not found.", reply_markup=back_btn)