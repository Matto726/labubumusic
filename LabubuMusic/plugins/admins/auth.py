from pyrogram import filters
from pyrogram.types import Message
from LabubuMusic import matto_bot
from LabubuMusic.utils import extract_user, int_to_alpha
from LabubuMusic.utils.database import (
    delete_authuser,
    get_authuser,
    get_authuser_names,
    save_authuser,
)
from LabubuMusic.utils.decorators import AdminActual, language
from LabubuMusic.utils.inline import close_markup
from config import BANNED_USERS, adminlist

@matto_bot.on_message(filters.command("auth") & filters.group & ~BANNED_USERS)
@AdminActual
async def authorize_user(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])

    target_user = await extract_user(message)
    user_token = await int_to_alpha(target_user.id)
    chat_id = message.chat.id
    
    current_auths = await get_authuser_names(chat_id)
    
    if len(current_auths) >= 25:
        return await message.reply_text(_["auth_1"])
        
    if user_token in current_auths:
        return await message.reply_text(_["auth_3"].format(target_user.mention))

    auth_data = {
        "auth_user_id": target_user.id,
        "auth_name": target_user.first_name,
        "admin_id": message.from_user.id,
        "admin_name": message.from_user.first_name,
    }

    admin_cache = adminlist.get(chat_id)
    if admin_cache and target_user.id not in admin_cache:
        admin_cache.append(target_user.id)
        
    await save_authuser(chat_id, user_token, auth_data)
    await message.reply_text(_["auth_2"].format(target_user.mention))

@matto_bot.on_message(filters.command("unauth") & filters.group & ~BANNED_USERS)
@AdminActual
async def unauthorize_user(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])
        
    target_user = await extract_user(message)
    user_token = await int_to_alpha(target_user.id)
    chat_id = message.chat.id
    
    is_deleted = await delete_authuser(chat_id, user_token)
    
    admin_cache = adminlist.get(chat_id)
    if admin_cache and target_user.id in admin_cache:
        admin_cache.remove(target_user.id)
        
    response = _["auth_4"] if is_deleted else _["auth_5"]
    await message.reply_text(response.format(target_user.mention))

@matto_bot.on_message(filters.command(["authlist", "authusers"]) & filters.group & ~BANNED_USERS)
@language
async def list_auth_users(client, message: Message, _):
    chat_id = message.chat.id
    auth_list = await get_authuser_names(chat_id)
    
    if not auth_list:
        return await message.reply_text(_["setting_4"])
        
    status_msg = await message.reply_text(_["auth_6"])
    report = _["auth_7"].format(message.chat.title)
    
    count = 0
    for token in auth_list:
        data = await get_authuser(chat_id, token)
        
        try:
            u_obj = await matto_bot.get_users(data["auth_user_id"])
            user_name = u_obj.first_name
            count += 1
        except:
            continue
            
        report += f"{count}➤ {user_name}[<code>{data['auth_user_id']}</code>]\n"
        report += f"   {_['auth_8']} {data['admin_name']}[<code>{data['admin_id']}</code>]\n\n"
        
    await status_msg.edit_text(report, reply_markup=close_markup(_))