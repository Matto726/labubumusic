from pyrogram import filters, types
from LabubuMusic import matto_bot
from LabubuMusic.core.call import Matto
from LabubuMusic.misc import SUDO_USERS, db
from LabubuMusic.utils import AdminRightsCheck
from LabubuMusic.utils.database import is_active_chat, is_nonadmin_chat
from LabubuMusic.utils.decorators.language import languageCB
from LabubuMusic.utils.inline import close_markup, speed_markup
from config import BANNED_USERS, adminlist

speed_lock = []

@matto_bot.on_message(filters.command(["cspeed", "speed", "cslow", "slow", "playback", "cplayback"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def playback_control(client, message: types.Message, _, chat_id):
    queue = db.get(chat_id)
    if not queue:
        return await message.reply_text(_["queue_2"])
        
    if int(queue[0]["seconds"]) == 0 or "downloads" not in queue[0]["file"]:
        return await message.reply_text(_["admin_27"])
        
    await message.reply_text(
        text=_["admin_28"].format(matto_bot.mention),
        reply_markup=speed_markup(_, chat_id)
    )

@matto_bot.on_callback_query(filters.regex("SpeedUP") & ~BANNED_USERS)
@languageCB
async def speed_callback_handler(client, cb, _):
    meta = cb.data.strip().split(None, 1)[1]
    chat_str, speed_val = meta.split("|")
    chat_id = int(chat_str)

    if not await is_active_chat(chat_id):
        return await cb.answer(_["general_5"], show_alert=True)

    is_non_admin = await is_nonadmin_chat(cb.message.chat.id)
    if not is_non_admin and cb.from_user.id not in SUDO_USERS:
        admins = adminlist.get(cb.message.chat.id)
        if not admins or cb.from_user.id not in admins:
             return await cb.answer(_["admin_14"], show_alert=True)

    queue = db.get(chat_id)
    if not queue:
        return await cb.answer(_["queue_2"], show_alert=True)
        
    if int(queue[0]["seconds"]) == 0 or "downloads" not in queue[0]["file"]:
        return await cb.answer(_["admin_27"], show_alert=True)

    current_speed = queue[0].get("speed", "1.0")
    if str(current_speed) == str(speed_val):
        if str(speed_val) == "1.0":
            return await cb.answer(_["admin_29"], show_alert=True)

    if chat_id in speed_lock:
        return await cb.answer(_["admin_30"], show_alert=True)
        
    speed_lock.append(chat_id)
    
    try:
        await cb.answer(_["admin_31"])
    except:
        pass
        
    status_msg = await cb.edit_message_text(_["admin_32"].format(cb.from_user.mention))
    
    try:
        await Matto.speedup_stream(chat_id, queue[0]["file"], speed_val, queue)
    except:
        if chat_id in speed_lock: speed_lock.remove(chat_id)
        return await status_msg.edit_text(_["admin_33"], reply_markup=close_markup(_))
        
    if chat_id in speed_lock: speed_lock.remove(chat_id)
    
    await status_msg.edit_text(
        _["admin_34"].format(speed_val, cb.from_user.mention),
        reply_markup=close_markup(_)
    )