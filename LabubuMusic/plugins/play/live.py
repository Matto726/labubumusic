from pyrogram import filters
from LabubuMusic import YouTube, matto_bot
from LabubuMusic.utils.channelplay import get_channeplayCB
from LabubuMusic.utils.decorators.language import languageCB
from LabubuMusic.utils.stream.stream import stream
from config import BANNED_USERS

@matto_bot.on_callback_query(filters.regex("LiveStream") & ~BANNED_USERS)
@languageCB
async def stream_live_content(client, cb, _):
    data_parts = cb.data.strip().split(None, 1)[1]
    vid_id, user_id_str, mode, cplay_mode, force_mode = data_parts.split("|")
    
    if cb.from_user.id != int(user_id_str):
        try:
            return await cb.answer(_["playcb_1"], show_alert=True)
        except:
            return

    try:
        chat_id, channel_name = await get_channeplayCB(_, cplay_mode, cb)
    except:
        return

    is_video = True if mode == "v" else None
    requester = cb.from_user.first_name
    
    await cb.message.delete()
    try:
        await cb.answer()
    except:
        pass

    status_msg = await cb.message.reply_text(
        _["play_2"].format(channel_name) if channel_name else _["play_1"]
    )

    try:
        track_data, _ = await YouTube.track(vid_id, True)
    except:
        return await status_msg.edit_text(_["play_3"])

    force_play = True if force_mode == "f" else None

    if not track_data["duration_min"]:
        try:
            await stream(
                _,
                status_msg,
                int(user_id_str),
                track_data,
                chat_id,
                requester,
                cb.message.chat.id,
                is_video,
                streamtype="live",
                forceplay=force_play,
            )
        except Exception as err:
            err_name = type(err).__name__
            msg = err if err_name == "AssistantErr" else _["general_2"].format(err_name)
            return await status_msg.edit_text(msg)
    else:
        return await status_msg.edit_text("» This is not a live stream.")
    
    await status_msg.delete()