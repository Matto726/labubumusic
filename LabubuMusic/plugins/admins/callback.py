import asyncio
import time
import psutil
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from LabubuMusic import YouTube, matto_bot
from LabubuMusic.core.call import Matto
from LabubuMusic.misc import SUDO_USERS, db
from LabubuMusic.utils import bot_sys_stats
from LabubuMusic.utils.database import (
    get_active_chats, get_lang, get_upvote_count, is_active_chat,
    is_music_playing, is_nonadmin_chat, music_off, music_on, set_loop
)
from LabubuMusic.utils.decorators.language import languageCB
from LabubuMusic.utils.formatters import seconds_to_min
from LabubuMusic.utils.inline import close_markup, stream_markup, stream_markup_timer
from LabubuMusic.utils.inline.help import (
    help_pannel_page1, help_pannel_page2, 
    help_pannel_page3, help_pannel_page4
)
from LabubuMusic.utils.inline.start import about_panel, owner_panel
from LabubuMusic.utils.stream.autoclear import auto_clean
from LabubuMusic.utils.thumbnails import gen_thumb
import config
from config import (
    BANNED_USERS, SOUNCLOUD_IMG_URL, STREAM_IMG_URL,
    TELEGRAM_AUDIO_URL, TELEGRAM_VIDEO_URL, adminlist,
    confirmer, votemode, SUPPORT_GROUP
)
from strings import get_string

markup_cache = {}
voting_cache = {}

@matto_bot.on_callback_query(filters.regex("help_page") & ~BANNED_USERS)
async def help_navigation(client, cb: CallbackQuery):
    page_map = {
        "help_page_1": help_pannel_page1,
        "help_page_2": help_pannel_page2,
        "help_page_3": help_pannel_page3,
        "help_page_4": help_pannel_page4
    }
    
    try:
        lang = await get_lang(cb.message.chat.id)
        txt = get_string(lang)
    except:
        txt = get_string("en")

    target_page = page_map.get(cb.data)
    if target_page:
        await cb.message.edit_caption(
            caption=txt["help_1"].format(SUPPORT_GROUP),
            reply_markup=target_page(txt, START=True)
        )

@matto_bot.on_callback_query(filters.regex("fork_repo"))
async def fork_repo_cb(client, query):
   
    info_text = (
        "🔧 <b>Labubu Music: Powerful & Fast 🔥</b>"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="settingsback_helper")]
    ])
    
    await query.message.edit_text(info_text, disable_web_page_preview=True, reply_markup=buttons)

@matto_bot.on_callback_query(filters.regex("(about_page|owner_page)") & ~BANNED_USERS)
async def info_pages_cb(client, cb):
    try:
        txt = get_string("en")
        await cb.answer()
        
        if cb.data == "about_page":
            panel = about_panel(txt)
        else:
            panel = owner_panel(txt)
            
        await cb.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(panel))
    except Exception as e:
        await cb.answer(f"❌ Error: {e}", show_alert=True)

@matto_bot.on_callback_query(filters.regex("ping_status"))
async def system_stats_cb(client, cb: CallbackQuery):
    status_msg = await cb.message.reply_text("🔄 Checking System Status...")
    
    start_t = time.time()
    try:
        await Matto.ping()
    except:
        pass
    latency = round((time.time() - start_t) * 1000)
    
    try:
        uptime_str, cpu_usage, ram_usage, disk_usage = await bot_sys_stats()
    except:
        uptime_str = "Unknown"
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

    color_ind = "🟢" if latency < 100 else "🟡" if latency < 300 else "🔴"
    
    report = (
        f"📡 **Ping:** {latency}ms {color_ind}\n"
        f"⏱ **Uptime:** {uptime_str}\n"
        f"💾 **Disk:** {disk_usage}%\n"
        f"📈 **RAM:** {ram_usage}%\n"
        f"🖥 **CPU:** {cpu_usage}%"
    )
    
    await status_msg.edit_text(report)
    await asyncio.sleep(8)
    await status_msg.delete()

@matto_bot.on_callback_query(filters.regex("ADMIN") & ~BANNED_USERS)
@languageCB
async def admin_control_cb(client, cb, _):
    data_parts = cb.data.strip().split(None, 1)[1]
    cmd, meta = data_parts.split("|")
    
    if "_" in meta:
        chat_id_str, counter = meta.split("_")
        chat_id = int(chat_id_str)
    else:
        chat_id = int(meta)
        counter = None

    if not await is_active_chat(chat_id):
        return await cb.answer(_["general_5"], show_alert=True)

    user_mention = cb.from_user.mention

    # Permission Check
    if cmd != "UpVote":
        is_admin_mode = not await is_nonadmin_chat(cb.message.chat.id)
        if is_admin_mode:
            if cb.from_user.id not in SUDO_USERS:
                chat_admins = adminlist.get(cb.message.chat.id)
                if not chat_admins:
                    return await cb.answer(_["admin_13"], show_alert=True)
                if cb.from_user.id not in chat_admins:
                    return await cb.answer(_["admin_14"], show_alert=True)

    if cmd == "UpVote":
        await handle_upvote(cb, chat_id, counter, _)
    elif cmd == "Pause":
        await handle_pause(cb, chat_id, user_mention, _)
    elif cmd == "Resume":
        await handle_resume(cb, chat_id, user_mention, _)
    elif cmd in ["Stop", "End"]:
        await handle_stop(cb, chat_id, user_mention, _)
    elif cmd in ["Skip", "Replay"]:
        await handle_skip_replay(cb, chat_id, user_mention, cmd, _)

async def handle_upvote(cb, chat_id, counter, _):
    votemode.setdefault(chat_id, {})
    voting_cache.setdefault(chat_id, {})

    msg_id = cb.message.id
    current_voters = voting_cache[chat_id].setdefault(msg_id, [])
    current_count = votemode[chat_id].setdefault(msg_id, 0)

    uid = cb.from_user.id
    
    if uid in current_voters:
        current_voters.remove(uid)
        votemode[chat_id][msg_id] -= 1
    else:
        current_voters.append(uid)
        votemode[chat_id][msg_id] += 1
        
    required_votes = await get_upvote_count(chat_id)
    current_votes = votemode[chat_id][msg_id]
    
    if current_votes >= required_votes:
        votemode[chat_id][msg_id] = required_votes
        try:
            req_info = confirmer[chat_id][msg_id]
            curr_track = db[chat_id][0]
            if curr_track["vidid"] != req_info["vidid"] or curr_track["file"] != req_info["file"]:
                 return await cb.edit_message_text(_["admin_35"])
        except:
             return await cb.edit_message_text(_["admin_36"])
        
        try:
            await cb.edit_message_text(_["admin_37"].format(required_votes))
        except:
            pass
    else:
        if uid in current_voters:
            await cb.answer(_["admin_38"], show_alert=True)
        else:
            await cb.answer(_["admin_39"], show_alert=True)
            
        btn = InlineKeyboardMarkup([[
            InlineKeyboardButton(text=f"👍 {current_votes}", callback_data=f"ADMIN  UpVote|{chat_id}_{counter}")
        ]])
        await cb.answer(_["admin_40"], show_alert=True)
        await cb.edit_message_reply_markup(reply_markup=btn)

async def handle_pause(cb, chat_id, mention, _):
    if not await is_music_playing(chat_id):
        return await cb.answer(_["admin_1"], show_alert=True)
    await cb.answer()
    await music_off(chat_id)
    await Matto.pause_stream(chat_id)
    await cb.message.reply_text(_["admin_2"].format(mention), reply_markup=close_markup(_))

async def handle_resume(cb, chat_id, mention, _):
    if await is_music_playing(chat_id):
        return await cb.answer(_["admin_3"], show_alert=True)
    await cb.answer()
    await music_on(chat_id)
    await Matto.resume_stream(chat_id)
    await cb.message.reply_text(_["admin_4"].format(mention), reply_markup=close_markup(_))

async def handle_stop(cb, chat_id, mention, _):
    await cb.answer()
    await Matto.stop_stream(chat_id)
    await set_loop(chat_id, 0)
    await cb.message.reply_text(_["admin_5"].format(mention), reply_markup=close_markup(_))
    try:
        await cb.message.delete()
    except:
        pass

async def handle_skip_replay(cb, chat_id, mention, command, _):
    queue = db.get(chat_id)
    if not queue:
        return await cb.answer("No music in queue!", show_alert=True)
        
    await cb.answer()
    
    if command == "Skip":
        skip_text = f"➻ Stream Skipped ⏭\n│ \n└By : {mention}"
        try:
            popped = queue.pop(0)
            if popped:
                await auto_clean(popped)
            
            if not queue:
                await cb.edit_message_text(skip_text)
                await cb.message.reply_text(
                    _["admin_6"].format(mention, cb.message.chat.title),
                    reply_markup=close_markup(_)
                )
                return await Matto.stop_stream(chat_id)
        except:
            return
    else:
        skip_text = f"➻ Stream Replayed ⏮\n│ \n└By : {mention}"

    if not queue:
         return await cb.edit_message_text("Queue is empty!")
    track = queue[0]
    track_file = track["file"]
    vid_id = track["vidid"]
    is_video = (track["streamtype"] == "video")

    db[chat_id][0]["played"] = 0
    if track.get("old_dur"):
        db[chat_id][0]["dur"] = track["old_dur"]
        db[chat_id][0]["seconds"] = track["old_second"]
        db[chat_id][0]["speed"] = 1.0
        db[chat_id][0]["speed_path"] = None

    if "live_" in track_file:
        status, link = await YouTube.video(vid_id, True)
        if status == 0:
            return await cb.message.reply_text(_["admin_7"].format(track["title"]))
        
        await Matto.skip_stream(chat_id, link, video=is_video, image=await YouTube.thumbnail(vid_id, True))
        
        btn = stream_markup(_, chat_id)
        msg = await cb.message.reply_photo(
            photo=await gen_thumb(vid_id),
            caption=_["stream_1"].format(f"https://t.me/{matto_bot.username}?start=info_{vid_id}", track["title"][:23], track["dur"], track["by"]),
            reply_markup=InlineKeyboardMarkup(btn)
        )
        db[chat_id][0]["mystic"] = msg
        db[chat_id][0]["markup"] = "tg"
        await cb.edit_message_text(skip_text, reply_markup=close_markup(_))

    elif "vid_" in track_file:
        load_msg = await cb.message.reply_text(_["call_7"], disable_web_page_preview=True)
        fpath, _ = await YouTube.download(vid_id, load_msg, videoid=True, video=is_video)
        await Matto.skip_stream(chat_id, fpath, video=is_video, image=await YouTube.thumbnail(vid_id, True))
        
        btn = stream_markup(_, chat_id)
        msg = await cb.message.reply_photo(
            photo=await gen_thumb(vid_id),
            caption=_["stream_1"].format(f"https://t.me/{matto_bot.username}?start=info_{vid_id}", track["title"][:23], track["dur"], track["by"]),
            reply_markup=InlineKeyboardMarkup(btn)
        )
        db[chat_id][0]["mystic"] = msg
        db[chat_id][0]["markup"] = "stream"
        await cb.edit_message_text(skip_text, reply_markup=close_markup(_))
        await load_msg.delete()

    elif "index_" in track_file:
        await Matto.skip_stream(chat_id, vid_id, video=is_video)
        btn = stream_markup(_, chat_id)
        msg = await cb.message.reply_photo(
            photo=STREAM_IMG_URL,
            caption=_["stream_2"].format(track["by"]),
            reply_markup=InlineKeyboardMarkup(btn)
        )
        db[chat_id][0]["mystic"] = msg
        db[chat_id][0]["markup"] = "tg"
        await cb.edit_message_text(skip_text, reply_markup=close_markup(_))

    else:
        img = None
        if vid_id not in ["telegram", "soundcloud"]:
            try:
                img = await YouTube.thumbnail(vid_id, True)
            except:
                pass
        
        await Matto.skip_stream(chat_id, track_file, video=is_video, image=img)
        
        btn = stream_markup(_, chat_id)

        if vid_id == "telegram":
            display_img = TELEGRAM_AUDIO_URL if track["streamtype"] == "audio" else TELEGRAM_VIDEO_URL
        elif vid_id == "soundcloud":
            display_img = SOUNCLOUD_IMG_URL
        else:
            display_img = await gen_thumb(vid_id)
            
        caption_link = config.SUPPORT_GROUP if vid_id in ["telegram", "soundcloud"] else f"https://t.me/{matto_bot.username}?start=info_{vid_id}"
            
        msg = await cb.message.reply_photo(
            photo=display_img,
            caption=_["stream_1"].format(caption_link, track["title"][:23], track["dur"], track["by"]),
            reply_markup=InlineKeyboardMarkup(btn)
        )
        db[chat_id][0]["mystic"] = msg
        db[chat_id][0]["markup"] = "tg" if vid_id in ["telegram", "soundcloud"] else "stream"
        await cb.edit_message_text(skip_text, reply_markup=close_markup(_))

async def update_player_ui():
    while True:
        await asyncio.sleep(7)
        try:
            active_list = await get_active_chats()
            for chat in active_list:
                if not await is_music_playing(chat):
                    continue
                
                track_data = db.get(chat)
                if not track_data or not track_data[0].get("mystic"):
                    continue
                    
                track = track_data[0]
                if int(track["seconds"]) == 0:
                    continue
                
                msg_obj = track["mystic"]

                if msg_obj.id not in markup_cache.get(chat, {}):
                     pass

                try:
                    lang = await get_lang(chat)
                    txt = get_string(lang)
                except:
                    txt = get_string("en")
                    
                try:
                    new_markup = stream_markup_timer(
                        txt, chat, 
                        seconds_to_min(track["played"]), 
                        track["dur"]
                    )
                    await msg_obj.edit_reply_markup(reply_markup=InlineKeyboardMarkup(new_markup))
                except:
                    continue
        except:
            continue

asyncio.create_task(update_player_ui())