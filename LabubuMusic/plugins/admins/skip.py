from pyrogram import filters, types, InlineKeyboardMarkup
from LabubuMusic import YouTube, matto_bot
from LabubuMusic.core.call import Matto
from LabubuMusic.misc import db
from LabubuMusic.utils.database import get_loop
from LabubuMusic.utils.decorators import AdminRightsCheck
from LabubuMusic.utils.inline import close_markup, stream_markup
from LabubuMusic.utils.stream.autoclear import auto_clean
from LabubuMusic.utils.thumbnails import gen_thumb
from config import BANNED_USERS, STREAM_IMG_URL, TELEGRAM_AUDIO_URL, TELEGRAM_VIDEO_URL, SOUNCLOUD_IMG_URL, SUPPORT_GROUP

@matto_bot.on_message(filters.command(["skip", "cskip", "next", "cnext"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def skip_track(client, message: types.Message, _, chat_id):
    queue = db.get(chat_id)
    if not queue:
        return await message.reply_text(_["queue_2"])

    if len(message.command) > 1:
        if await get_loop(chat_id) != 0:
            return await message.reply_text(_["admin_8"])
            
        arg = message.text.split(None, 1)[1].strip()
        if arg.isnumeric():
            count = int(arg)
            q_len = len(queue)
            
            if q_len > 2:
                available_skips = q_len - 1
                if 1 <= count <= available_skips:
                    for _ in range(count):
                        popped = queue.pop(0)
                        await auto_clean(popped)
                        if not queue:
                            await Matto.stop_stream(chat_id)
                            return await message.reply_text(
                                _["admin_6"].format(message.from_user.mention, message.chat.title),
                                reply_markup=close_markup(_)
                            )
                else:
                    return await message.reply_text(_["admin_11"].format(available_skips))
            else:
                return await message.reply_text(_["admin_10"])
        else:
            return await message.reply_text(_["admin_9"])

    else:
        try:
            popped = queue.pop(0)
            if popped: await auto_clean(popped)
            
            if not queue:
                await Matto.stop_stream(chat_id)
                return await message.reply_text(
                    _["admin_6"].format(message.from_user.mention, message.chat.title),
                    reply_markup=close_markup(_)
                )
        except:
             return

    next_track = queue[0]
    fname = next_track["file"]
    vid = next_track["vidid"]
    is_vid = (next_track["streamtype"] == "video")

    db[chat_id][0]["played"] = 0
    if next_track.get("old_dur"):
        db[chat_id][0]["dur"] = next_track["old_dur"]
        db[chat_id][0]["seconds"] = next_track["old_second"]
        db[chat_id][0]["speed"] = 1.0
        db[chat_id][0]["speed_path"] = None

    if "live_" in fname:
        ok, link = await YouTube.video(vid, True)
        if ok == 0: return await message.reply_text(_["admin_7"].format(next_track["title"]))
        
        await Matto.skip_stream(chat_id, link, video=is_vid, image=await YouTube.thumbnail(vid, True))
        
        markup = stream_markup(_, chat_id)
        msg = await message.reply_photo(
            photo=await gen_thumb(vid),
            caption=_["stream_1"].format(f"https://t.me/{matto_bot.username}?start=info_{vid}", next_track["title"][:23], next_track["dur"], next_track["by"]),
            reply_markup=InlineKeyboardMarkup(markup)
        )
        db[chat_id][0]["mystic"] = msg
        db[chat_id][0]["markup"] = "tg"

    elif "vid_" in fname:
        status = await message.reply_text(_["call_7"], disable_web_page_preview=True)
        fpath, _ = await YouTube.download(vid, status, videoid=True, video=is_vid)
        await Matto.skip_stream(chat_id, fpath, video=is_vid, image=await YouTube.thumbnail(vid, True))
        
        markup = stream_markup(_, chat_id)
        msg = await message.reply_photo(
            photo=await gen_thumb(vid),
            caption=_["stream_1"].format(f"https://t.me/{matto_bot.username}?start=info_{vid}", next_track["title"][:23], next_track["dur"], next_track["by"]),
            reply_markup=InlineKeyboardMarkup(markup)
        )
        db[chat_id][0]["mystic"] = msg
        db[chat_id][0]["markup"] = "stream"
        await status.delete()

    elif "index_" in fname:
        await Matto.skip_stream(chat_id, vid, video=is_vid)
        markup = stream_markup(_, chat_id)
        msg = await message.reply_photo(
            photo=STREAM_IMG_URL,
            caption=_["stream_2"].format(next_track["by"]),
            reply_markup=InlineKeyboardMarkup(markup)
        )
        db[chat_id][0]["mystic"] = msg
        db[chat_id][0]["markup"] = "tg"

    else:
        # Generic
        img = await YouTube.thumbnail(vid, True) if vid not in ["telegram", "soundcloud"] else None
        await Matto.skip_stream(chat_id, fname, video=is_vid, image=img)
        
        markup = stream_markup(_, chat_id)
        
        if vid == "telegram":
            pic = TELEGRAM_AUDIO_URL if next_track["streamtype"] == "audio" else TELEGRAM_VIDEO_URL
            link = SUPPORT_GROUP
        elif vid == "soundcloud":
            pic = SOUNCLOUD_IMG_URL
            link = SUPPORT_GROUP
        else:
            pic = await gen_thumb(vid)
            link = f"https://t.me/{matto_bot.username}?start=info_{vid}"

        msg = await message.reply_photo(
            photo=pic,
            caption=_["stream_1"].format(link, next_track["title"][:23], next_track["dur"], next_track["by"]),
            reply_markup=InlineKeyboardMarkup(markup)
        )
        db[chat_id][0]["mystic"] = msg
        db[chat_id][0]["markup"] = "tg" if vid in ["telegram", "soundcloud"] else "stream"