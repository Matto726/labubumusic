from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.errors import MessageNotModified
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from LabubuMusic import matto_bot
from LabubuMusic.utils.database import (
    add_nonadmin_chat, get_authuser, get_authuser_names,
    get_playmode, get_playtype, get_upvote_count,
    is_nonadmin_chat, is_skipmode, remove_nonadmin_chat,
    set_playmode, set_playtype, set_upvotes,
    skip_off, skip_on,
)
from LabubuMusic.utils import bot_sys_stats
from LabubuMusic.utils.decorators.admins import ActualAdminCB
from LabubuMusic.utils.decorators.language import language, languageCB
from LabubuMusic.utils.inline.settings import (
    auth_users_markup, playmode_users_markup,
    setting_markup, vote_mode_markup,
)
from LabubuMusic.utils.inline.start import private_panel
from config import BANNED_USERS, OWNER_ID

@matto_bot.on_message(filters.command(["settings", "setting"]) & filters.group & ~BANNED_USERS)
@language
async def settings_panel(client, message: Message, _):
    btn = setting_markup(_)
    await message.reply_text(
        _["setting_1"].format(matto_bot.mention, message.chat.id, message.chat.title),
        reply_markup=InlineKeyboardMarkup(btn),
    )

@matto_bot.on_callback_query(filters.regex("settings_helper") & ~BANNED_USERS)
@languageCB
async def settings_refresh(client, cb: CallbackQuery, _):
    try:
        await cb.answer(_["set_cb_5"])
    except:
        pass
    btn = setting_markup(_)
    await cb.edit_message_text(
        _["setting_1"].format(matto_bot.mention, cb.message.chat.id, cb.message.chat.title),
        reply_markup=InlineKeyboardMarkup(btn),
    )

@matto_bot.on_callback_query(filters.regex("settingsback_helper") & ~BANNED_USERS)
@languageCB
async def settings_back(client, cb: CallbackQuery, _):
    try:
        await cb.answer()
    except:
        pass
        
    if cb.message.chat.type == ChatType.PRIVATE:
        await matto_bot.resolve_peer(OWNER_ID)
        btn = private_panel(_)
        uptime, cpu, ram, disk = await bot_sys_stats()
        await cb.edit_message_text(
            _["start_2"].format(cb.from_user.mention, matto_bot.mention, uptime, disk, cpu, ram),
            reply_markup=InlineKeyboardMarkup(btn),
        )
    else:
        btn = setting_markup(_)
        await cb.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))

@matto_bot.on_callback_query(
    filters.regex(r"^(SEARCHANSWER|PLAYMODEANSWER|PLAYTYPEANSWER|AUTHANSWER|ANSWERVOMODE|VOTEANSWER|PM|AU|VM)$")
    & ~BANNED_USERS
)
@languageCB
async def settings_info_handlers(client, cb, _):
    cmd = cb.matches[0].group(1)
    
    alerts = {
        "SEARCHANSWER": _["setting_2"],
        "PLAYMODEANSWER": _["setting_5"],
        "PLAYTYPEANSWER": _["setting_6"],
        "AUTHANSWER": _["setting_3"],
        "VOTEANSWER": _["setting_8"],
    }
    
    if cmd in alerts:
        try:
            return await cb.answer(alerts[cmd], show_alert=True)
        except:
            return

    if cmd == "ANSWERVOMODE":
        count = await get_upvote_count(cb.message.chat.id)
        return await cb.answer(_["setting_9"].format(count), show_alert=True)

    if cmd == "PM":
        try: await cb.answer(_["set_cb_2"], show_alert=True)
        except: pass
        
        pmode = await get_playmode(cb.message.chat.id)
        ptype = await get_playtype(cb.message.chat.id)
        is_admin_only = not await is_nonadmin_chat(cb.message.chat.id)
        
        direct_flag = True if pmode == "Direct" else None
        group_flag = True if is_admin_only else None
        playtype_flag = None if ptype == "Everyone" else True
        
        btn = playmode_users_markup(_, direct_flag, group_flag, playtype_flag)
        
    elif cmd == "AU":
        try: await cb.answer(_["set_cb_1"], show_alert=True)
        except: pass
        
        is_admin_only = not await is_nonadmin_chat(cb.message.chat.id)
        btn = auth_users_markup(_, True if is_admin_only else None)
        
    elif cmd == "VM":
        skip_mode = await is_skipmode(cb.message.chat.id)
        vote_count = await get_upvote_count(cb.message.chat.id)
        btn = vote_mode_markup(_, vote_count, skip_mode)
        
    try:
        await cb.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass

@matto_bot.on_callback_query(filters.regex("FERRARIUDTI") & ~BANNED_USERS)
@ActualAdminCB
async def upvote_threshold_change(client, cb, _):
    meta = cb.data.strip().split(None, 1)[1]
    
    if not await is_skipmode(cb.message.chat.id):
        return await cb.answer(_["setting_10"], show_alert=True)
        
    curr_votes = await get_upvote_count(cb.message.chat.id)
    
    if meta == "M":
        new_votes = max(curr_votes - 2, 2)
        if new_votes == 0:
             return await cb.answer(_["setting_11"], show_alert=True)
    else:
        new_votes = min(curr_votes + 2, 15)
        if new_votes >= 17:
             return await cb.answer(_["setting_12"], show_alert=True)
             
    await set_upvotes(cb.message.chat.id, new_votes)
    
    btn = vote_mode_markup(_, new_votes, True)
    try:
        await cb.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass

@matto_bot.on_callback_query(filters.regex(r"^(MODECHANGE|CHANNELMODECHANGE|PLAYTYPECHANGE)$") & ~BANNED_USERS)
@ActualAdminCB
async def playmode_toggle(client, cb, _):
    cmd = cb.matches[0].group(1)
    chat_id = cb.message.chat.id
    
    if cmd == "CHANNELMODECHANGE":
        if not await is_nonadmin_chat(chat_id):
            await add_nonadmin_chat(chat_id)
            group_flag = None
        else:
            await remove_nonadmin_chat(chat_id)
            group_flag = True

        pmode = await get_playmode(chat_id)
        ptype = await get_playtype(chat_id)
        direct_flag = True if pmode == "Direct" else None
        playtype_flag = None if ptype == "Everyone" else True
        
    elif cmd == "MODECHANGE":
        try: await cb.answer(_["set_cb_3"], show_alert=True)
        except: pass
        
        pmode = await get_playmode(chat_id)
        if pmode == "Direct":
            await set_playmode(chat_id, "Inline")
            direct_flag = None
        else:
            await set_playmode(chat_id, "Direct")
            direct_flag = True

        is_admin_only = not await is_nonadmin_chat(chat_id)
        group_flag = True if is_admin_only else None
        ptype = await get_playtype(chat_id)
        playtype_flag = False if ptype == "Everyone" else True
        
    elif cmd == "PLAYTYPECHANGE":
        try: await cb.answer(_["set_cb_3"], show_alert=True)
        except: pass
        
        ptype = await get_playtype(chat_id)
        if ptype == "Everyone":
            await set_playtype(chat_id, "Admin")
            playtype_flag = False
        else:
            await set_playtype(chat_id, "Everyone")
            playtype_flag = True

        pmode = await get_playmode(chat_id)
        direct_flag = True if pmode == "Direct" else None
        is_admin_only = not await is_nonadmin_chat(chat_id)
        group_flag = True if is_admin_only else None

    btn = playmode_users_markup(_, direct_flag, group_flag, playtype_flag)
    try:
        await cb.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass

@matto_bot.on_callback_query(filters.regex(r"^(AUTH|AUTHLIST)$") & ~BANNED_USERS)
@ActualAdminCB
async def auth_settings_handler(client, cb, _):
    cmd = cb.matches[0].group(1)
    
    if cmd == "AUTHLIST":
        auth_users = await get_authuser_names(cb.message.chat.id)
        if not auth_users:
            return await cb.answer(_["setting_4"], show_alert=True)
        
        try: await cb.answer(_["set_cb_4"], show_alert=True)
        except: pass
        
        msg_text = _["auth_7"].format(cb.message.chat.title)
        
        for idx, token in enumerate(auth_users, 1):
            data = await get_authuser(cb.message.chat.id, token)
            try:
                u_obj = await matto_bot.get_users(data["auth_user_id"])
                name = u_obj.first_name
            except:
                continue
                
            msg_text += f"{idx}➤ {name}[<code>{data['auth_user_id']}</code>]\n"
            msg_text += f"   {_['auth_8']} {data['admin_name']}[<code>{data['admin_id']}</code>]\n\n"
            
        nav_btns = InlineKeyboardMarkup([[
            InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="AU"),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
        ]])
        
        return await cb.edit_message_text(msg_text, reply_markup=nav_btns)

    try: await cb.answer(_["set_cb_3"], show_alert=True)
    except: pass
    
    if cmd == "AUTH":
        if not await is_nonadmin_chat(cb.message.chat.id):
            await add_nonadmin_chat(cb.message.chat.id)
            btn = auth_users_markup(_)
        else:
            await remove_nonadmin_chat(cb.message.chat.id)
            btn = auth_users_markup(_, True)
            
        await cb.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))

@matto_bot.on_callback_query(filters.regex("VOMODECHANGE") & ~BANNED_USERS)
@ActualAdminCB
async def toggle_vote_mode(client, cb, _):
    try: await cb.answer(_["set_cb_3"], show_alert=True)
    except: pass
    
    mode_flag = None
    if await is_skipmode(cb.message.chat.id):
        await skip_off(cb.message.chat.id)
    else:
        mode_flag = True
        await skip_on(cb.message.chat.id)
        
    count = await get_upvote_count(cb.message.chat.id)
    btn = vote_mode_markup(_, count, mode_flag)
    
    await cb.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))