from pyrogram import filters, types
from LabubuMusic import YouTube, matto_bot
from LabubuMusic.core.call import Matto
from LabubuMusic.misc import db
from LabubuMusic.utils import AdminRightsCheck, seconds_to_min
from LabubuMusic.utils.inline import close_markup
from config import BANNED_USERS

@matto_bot.on_message(filters.command(["seek", "cseek", "seekback", "cseekback"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def seek_media(client, message: types.Message, _, chat_id):
    if len(message.command) < 2:
        return await message.reply_text(_["admin_20"])
        
    arg = message.text.split(None, 1)[1].strip()
    if not arg.isnumeric():
        return await message.reply_text(_["admin_21"])
        
    queue = db.get(chat_id)
    if not queue:
        return await message.reply_text(_["queue_2"])
        
    track = queue[0]
    total_sec = int(track["seconds"])
    if total_sec == 0:
        return await message.reply_text(_["admin_22"])

    seek_amount = int(arg)
    played_sec = int(track["played"])
    duration_str = track["dur"]
    
    is_seek_back = "back" in message.command[0]
    
    if is_seek_back:
        new_pos = max(played_sec - seek_amount, 0)
    else:
        new_pos = played_sec + seek_amount
        if (total_sec - new_pos) <= 10:
             return await message.reply_text(
                _["admin_23"].format(seconds_to_min(played_sec), duration_str),
                reply_markup=close_markup(_),
            )

    media_source = track["file"]
    if "vid_" in media_source:
        valid, media_source = await YouTube.video(track["vidid"], True)
        if valid == 0:
            return await message.reply_text(_["admin_22"])
            
    if track.get("speed_path"):
        media_source = track["speed_path"]
    
    if "index_" in media_source:
        media_source = track["vidid"]

    processing_msg = await message.reply_text(_["admin_24"])
    
    try:
        await Matto.seek_stream(
            chat_id,
            media_source,
            seconds_to_min(new_pos),
            duration_str,
            track["streamtype"],
        )
    except:
        return await processing_msg.edit_text(_["admin_26"], reply_markup=close_markup(_))

    db[chat_id][0]["played"] = new_pos
    
    await processing_msg.edit_text(
        _["admin_25"].format(seconds_to_min(new_pos), message.from_user.mention),
        reply_markup=close_markup(_),
    )