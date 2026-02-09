import random
import string
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto, Message

import config
from LabubuMusic import (
    Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, matto_bot
)
from LabubuMusic.core.call import Matto
from LabubuMusic.utils import seconds_to_min, time_to_seconds
from LabubuMusic.utils.channelplay import get_channeplayCB
from LabubuMusic.utils.decorators.language import languageCB
from LabubuMusic.utils.decorators.play import PlayWrapper
from LabubuMusic.utils.formatters import formats
from LabubuMusic.utils.inline import (
    botplaylist_markup, livestream_markup, playlist_markup,
    slider_markup, track_markup
)
from LabubuMusic.utils.logger import play_logs
from LabubuMusic.utils.stream.stream import stream
from config import BANNED_USERS, lyrical

@matto_bot.on_message(
    filters.command([
        "play", "vplay", "cplay", "cvplay", 
        "playforce", "vplayforce", "cplayforce", "cvplayforce"
    ]) & filters.group & ~BANNED_USERS
)
@PlayWrapper
async def handle_play_request(
    client, message: Message, _, 
    chat_id, video, channel, playmode, url, fplay
):
    status_msg = await message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )

    playlist_id = None
    is_slider = None
    playlist_type = None
    is_spotify = None
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    audio_file = (message.reply_to_message.audio or message.reply_to_message.voice) if message.reply_to_message else None
    video_file = (message.reply_to_message.video or message.reply_to_message.document) if message.reply_to_message else None

    if audio_file:
        if audio_file.file_size > 104857600:
            return await status_msg.edit_text(_["play_5"])
        
        if (audio_file.duration) > config.DURATION_LIMIT:
            return await status_msg.edit_text(
                _["play_6"].format(config.DURATION_LIMIT_MIN, matto_bot.mention)
            )
            
        fpath = await Telegram.get_filepath(audio=audio_file)
        if await Telegram.download(_, message, status_msg, fpath):
            details = {
                "title": await Telegram.get_filename(audio_file, audio=True),
                "link": await Telegram.get_link(message),
                "path": fpath,
                "dur": await Telegram.get_duration(audio_file, fpath),
            }
            try:
                await stream(
                    _, status_msg, user_id, details, chat_id, user_name,
                    message.chat.id, streamtype="telegram", forceplay=fplay
                )
            except Exception as e:
                return await status_msg.edit_text(_["general_2"].format(type(e).__name__))
            return await status_msg.delete()
        return

    elif video_file:
        if message.reply_to_message.document:
            try:
                if video_file.file_name.split(".")[-1].lower() not in formats:
                    return await status_msg.edit_text(_["play_7"].format(f"{' | '.join(formats)}"))
            except:
                return await status_msg.edit_text(_["play_7"].format(f"{' | '.join(formats)}"))
                
        if video_file.file_size > config.TG_VIDEO_FILESIZE_LIMIT:
            return await status_msg.edit_text(_["play_8"])
            
        fpath = await Telegram.get_filepath(video=video_file)
        if await Telegram.download(_, message, status_msg, fpath):
            details = {
                "title": await Telegram.get_filename(video_file),
                "link": await Telegram.get_link(message),
                "path": fpath,
                "dur": await Telegram.get_duration(video_file, fpath),
            }
            try:
                await stream(
                    _, status_msg, user_id, details, chat_id, user_name,
                    message.chat.id, video=True, streamtype="telegram", forceplay=fplay
                )
            except Exception as e:
                return await status_msg.edit_text(_["general_2"].format(type(e).__name__))
            return await status_msg.delete()
        return

    elif url:
        if await YouTube.exists(url):
            if "playlist" in url:
                try:
                    details = await YouTube.playlist(
                        url, config.PLAYLIST_FETCH_LIMIT, message.from_user.id
                    )
                except:
                    return await status_msg.edit_text(_["play_3"])
                
                streamtype = "playlist"
                playlist_type = "yt"
                playlist_id = (url.split("=")[1]).split("&")[0] if "&" in url else url.split("=")[1]
                img_url = config.PLAYLIST_IMG_URL
                caption_text = _["play_9"]
            else:
                try:
                    details, track_id = await YouTube.track(url)
                except:
                    return await status_msg.edit_text(_["play_3"])
                streamtype = "youtube"
                img_url = details["thumb"]
                caption_text = _["play_10"].format(details["title"], details["duration_min"])

        elif await Spotify.valid(url):
            is_spotify = True
            if not config.SPOTIFY_CLIENT_ID and not config.SPOTIFY_CLIENT_SECRET:
                return await status_msg.edit_text("» Spotify is not supported yet.")
                
            if "track" in url:
                try:
                    details, track_id = await Spotify.track(url)
                except:
                    return await status_msg.edit_text(_["play_3"])
                streamtype = "youtube"
                img_url = details["thumb"]
                caption_text = _["play_10"].format(details["title"], details["duration_min"])
            elif "playlist" in url:
                try:
                    details, playlist_id = await Spotify.playlist(url)
                except:
                    return await status_msg.edit_text(_["play_3"])
                streamtype = "playlist"
                playlist_type = "spplay"
                img_url = config.SPOTIFY_PLAYLIST_IMG_URL
                caption_text = _["play_11"].format(matto_bot.mention, message.from_user.mention)
            else:
                return await status_msg.edit_text(_["play_15"])

        elif await Apple.valid(url):
            if "album" in url:
                try:
                    details, track_id = await Apple.track(url)
                except:
                    return await status_msg.edit_text(_["play_3"])
                streamtype = "youtube"
                img_url = details["thumb"]
                caption_text = _["play_10"].format(details["title"], details["duration_min"])
            elif "playlist" in url:
                is_spotify = True
                try:
                    details, playlist_id = await Apple.playlist(url)
                except:
                    return await status_msg.edit_text(_["play_3"])
                streamtype = "playlist"
                playlist_type = "apple"
                caption_text = _["play_12"].format(matto_bot.mention, message.from_user.mention)
                img_url = url
            else:
                return await status_msg.edit_text(_["play_3"])

        elif await Resso.valid(url):
            try:
                details, track_id = await Resso.track(url)
            except:
                return await status_msg.edit_text(_["play_3"])
            streamtype = "youtube"
            img_url = details["thumb"]
            caption_text = _["play_10"].format(details["title"], details["duration_min"])

        elif await SoundCloud.valid(url):
            try:
                details, track_path = await SoundCloud.download(url)
            except:
                return await status_msg.edit_text(_["play_3"])
            if details["duration_sec"] > config.DURATION_LIMIT:
                return await status_msg.edit_text(_["play_6"].format(config.DURATION_LIMIT_MIN, matto_bot.mention))
            
            try:
                await stream(
                    _, status_msg, user_id, details, chat_id, user_name,
                    message.chat.id, streamtype="soundcloud", forceplay=fplay
                )
            except Exception as e:
                return await status_msg.edit_text(_["general_2"].format(type(e).__name__))
            return await status_msg.delete()

        else:
            try:
                await Matto.stream_call(url)
            except Exception as e:
                return await status_msg.edit_text(_["general_2"].format(type(e).__name__))
            
            await status_msg.edit_text(_["str_2"])
            try:
                await stream(
                    _, status_msg, user_id, url, chat_id, user_name,
                    message.chat.id, video=video, streamtype="index", forceplay=fplay
                )
            except Exception as e:
                return await status_msg.edit_text(_["general_2"].format(type(e).__name__))
            return await play_logs(message, streamtype="M3u8 or Index Link")

    else:
        if len(message.command) < 2:
            return await status_msg.edit_text(
                _["play_18"], reply_markup=InlineKeyboardMarkup(botplaylist_markup(_))
            )
        
        is_slider = True
        query = message.text.split(None, 1)[1].replace("-v", "")
        try:
            details, track_id = await YouTube.track(query)
        except:
            return await status_msg.edit_text(_["play_3"])
        streamtype = "youtube"

    if str(playmode) == "Direct":
        if not playlist_type:
            if details["duration_min"]:
                if time_to_seconds(details["duration_min"]) > config.DURATION_LIMIT:
                    return await status_msg.edit_text(_["play_6"].format(config.DURATION_LIMIT_MIN, matto_bot.mention))
            else:
                buttons = livestream_markup(
                    _, track_id, user_id, "v" if video else "a",
                    "c" if channel else "g", "f" if fplay else "d"
                )
                return await status_msg.edit_text(
                    _["play_13"], reply_markup=InlineKeyboardMarkup(buttons)
                )
        
        try:
            await stream(
                _, status_msg, user_id, details, chat_id, user_name,
                message.chat.id, video=video, streamtype=streamtype,
                spotify=is_spotify, forceplay=fplay
            )
        except Exception as e:
            return await status_msg.edit_text(_["general_2"].format(type(e).__name__))
        
        await status_msg.delete()
        return await play_logs(message, streamtype=streamtype)

    else:
        if playlist_type:
            unique_hash = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
            lyrical[unique_hash] = playlist_id
            buttons = playlist_markup(
                _, unique_hash, user_id, playlist_type,
                "c" if channel else "g", "f" if fplay else "d"
            )
            await status_msg.delete()
            await message.reply_photo(
                photo=img_url, caption=caption_text, reply_markup=InlineKeyboardMarkup(buttons)
            )
            return await play_logs(message, streamtype=f"Playlist : {playlist_type}")
        else:
            if is_slider:
                buttons = slider_markup(
                    _, track_id, user_id, query, 0,
                    "c" if channel else "g", "f" if fplay else "d"
                )
                await status_msg.delete()
                await message.reply_photo(
                    photo=details["thumb"],
                    caption=_["play_10"].format(details["title"].title(), details["duration_min"]),
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return await play_logs(message, streamtype="Searched on Youtube")
            else:
                buttons = track_markup(
                    _, track_id, user_id,
                    "c" if channel else "g", "f" if fplay else "d"
                )
                await status_msg.delete()
                await message.reply_photo(
                    photo=img_url, caption=caption_text, reply_markup=InlineKeyboardMarkup(buttons)
                )
                return await play_logs(message, streamtype="URL Searched Inline")

@matto_bot.on_callback_query(filters.regex("MusicStream") & ~BANNED_USERS)
@languageCB
async def music_callback_handler(client, cb, _):

    meta = cb.data.strip().split(None, 1)[1]
    vid_id, uid, mode, cplay, fplay = meta.split("|")
    
    if cb.from_user.id != int(uid):
        try: return await cb.answer(_["playcb_1"], show_alert=True)
        except: return

    try:
        chat_id, channel = await get_channeplayCB(_, cplay, cb)
    except:
        return

    requester = cb.from_user.first_name
    try:
        await cb.message.delete()
        await cb.answer()
    except:
        pass
        
    status_msg = await cb.message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )

    try:
        details, track_id = await YouTube.track(vid_id, True)
    except:
        return await status_msg.edit_text(_["play_3"])

    if details["duration_min"]:
        if time_to_seconds(details["duration_min"]) > config.DURATION_LIMIT:
            return await status_msg.edit_text(
                _["play_6"].format(config.DURATION_LIMIT_MIN, matto_bot.mention)
            )
    else:
        buttons = livestream_markup(
            _, track_id, cb.from_user.id, mode,
            "c" if cplay == "c" else "g", "f" if fplay else "d"
        )
        return await status_msg.edit_text(_["play_13"], reply_markup=InlineKeyboardMarkup(buttons))

    is_video = True if mode == "v" else None
    force_play = True if fplay == "f" else None

    try:
        await stream(
            _, status_msg, cb.from_user.id, details, chat_id, requester,
            cb.message.chat.id, is_video, streamtype="youtube", forceplay=force_play
        )
    except Exception as e:
        return await status_msg.edit_text(_["general_2"].format(type(e).__name__))
    
    return await status_msg.delete()

@matto_bot.on_callback_query(filters.regex("NandPlaylists") & ~BANNED_USERS)
@languageCB
async def playlist_handler(client, cb, _):
    meta = cb.data.strip().split(None, 1)[1]
    vid_id, uid, ptype, mode, cplay, fplay = meta.split("|")
    
    if cb.from_user.id != int(uid):
        try: return await cb.answer(_["playcb_1"], show_alert=True)
        except: return

    try:
        chat_id, channel = await get_channeplayCB(_, cplay, cb)
    except:
        return

    requester = cb.from_user.first_name
    await cb.message.delete()
    try: await cb.answer()
    except: pass
    
    status_msg = await cb.message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )
    
    playlist_id_real = lyrical.get(vid_id)
    is_video = True if mode == "v" else None
    force_play = True if fplay == "f" else None
    is_spotify = True

    try:
        if ptype == "yt":
            is_spotify = False
            result = await YouTube.playlist(playlist_id_real, config.PLAYLIST_FETCH_LIMIT, cb.from_user.id, True)
        elif ptype == "spplay":
            result, _ = await Spotify.playlist(playlist_id_real)
        elif ptype == "spalbum":
            result, _ = await Spotify.album(playlist_id_real)
        elif ptype == "spartist":
            result, _ = await Spotify.artist(playlist_id_real)
        elif ptype == "apple":
            result, _ = await Apple.playlist(playlist_id_real, True)
    except:
        return await status_msg.edit_text(_["play_3"])

    try:
        await stream(
            _, status_msg, int(uid), result, chat_id, requester,
            cb.message.chat.id, is_video, streamtype="playlist",
            spotify=is_spotify, forceplay=force_play
        )
    except Exception as e:
        return await status_msg.edit_text(_["general_2"].format(type(e).__name__))
        
    return await status_msg.delete()

@matto_bot.on_callback_query(filters.regex("slider") & ~BANNED_USERS)
@languageCB
async def slider_callback(client, cb, _):
    meta = cb.data.strip().split(None, 1)[1]
    direction, idx, query, uid, cplay, fplay = meta.split("|")
    
    if cb.from_user.id != int(uid):
        try: return await cb.answer(_["playcb_1"], show_alert=True)
        except: return

    current_idx = int(idx)
    new_idx = 0
    
    if direction == "F":
        new_idx = current_idx + 1 if current_idx < 9 else 0
    elif direction == "B":
        new_idx = current_idx - 1 if current_idx > 0 else 9
        
    try: await cb.answer(_["playcb_2"])
    except: pass
    
    title, duration, thumb, vid_id = await YouTube.slider(query, new_idx)
    buttons = slider_markup(_, vid_id, uid, query, new_idx, cplay, fplay)
    
    media_obj = InputMediaPhoto(
        media=thumb,
        caption=_["play_10"].format(title.title(), duration)
    )
    
    return await cb.edit_message_media(
        media=media_obj, reply_markup=InlineKeyboardMarkup(buttons)
    )