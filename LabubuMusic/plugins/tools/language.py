from pykeyboard import InlineKeyboard
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton

from LabubuMusic import matto_bot
from LabubuMusic.utils.database import get_lang, set_lang
from LabubuMusic.utils.decorators import ActualAdminCB, languageCB
from config import BANNED_USERS
from strings import get_string, languages_present

def build_lang_keyboard(_):
    keyboard = InlineKeyboard(row_width=2)
    
    buttons = [
        InlineKeyboardButton(
            text=languages_present[code],
            callback_data=f"set_lang:{code}"
        )
        for code in languages_present
    ]
    
    keyboard.add(*buttons)
    keyboard.row(
        InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="settingsback_helper"),
        InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close")
    )
    return keyboard

@matto_bot.on_callback_query(filters.regex("LG") & ~BANNED_USERS)
@languageCB
async def open_lang_menu(client, cb, _):
    try:
        await cb.answer()
    except:
        pass
        
    kb = build_lang_keyboard(_)
    await cb.edit_message_reply_markup(reply_markup=kb)

@matto_bot.on_callback_query(filters.regex(r"set_lang:(.*?)") & ~BANNED_USERS)
@ActualAdminCB
async def set_language_handler(client, cb, _):
    target_lang = cb.data.split(":")[1]
    current_lang = await get_lang(cb.message.chat.id)
    
    if current_lang == target_lang:
        return await cb.answer(_["lang_4"], show_alert=True)
        
    try:
        new_strings = get_string(target_lang)
        await set_lang(cb.message.chat.id, target_lang)
        
        await cb.answer(new_strings["lang_2"], show_alert=True)

        kb = build_lang_keyboard(new_strings)
        await cb.edit_message_reply_markup(reply_markup=kb)
        
    except Exception:
        return await cb.answer(_["lang_3"], show_alert=True)