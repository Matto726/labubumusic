from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from LabubuMusic import matto_bot
from LabubuMusic.misc import SUDO_USERS
from LabubuMusic.utils.database import add_sudo, remove_sudo
from LabubuMusic.utils.decorators.language import language
from LabubuMusic.utils.extraction import extract_user
from LabubuMusic.utils.functions import DevID
from config import OWNER_ID

def check_owner(user_id):
    return user_id == OWNER_ID or user_id == DevID

@matto_bot.on_message(filters.command("addsudo") & filters.user([OWNER_ID, DevID]))
@language
async def add_sudo_user(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])
        
    target = await extract_user(message)
    if not target:
        return
        
    if target.id in SUDO_USERS:
        return await message.reply_text(_["sudo_1"].format(target.mention))
        
    if await add_sudo(target.id):
        SUDO_USERS.add(target.id)
        await message.reply_text(_["sudo_2"].format(target.mention))
    else:
        await message.reply_text(_["sudo_8"])

@matto_bot.on_message(filters.command(["delsudo", "rmsudo"]) & filters.user([OWNER_ID, DevID]))
@language
async def remove_sudo_user(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])
        
    target = await extract_user(message)
    if not target:
        return
        
    if target.id not in SUDO_USERS:
        return await message.reply_text(_["sudo_3"].format(target.mention))
        
    if await remove_sudo(target.id):
        SUDO_USERS.discard(target.id)
        await message.reply_text(_["sudo_4"].format(target.mention))
    else:
        await message.reply_text(_["sudo_8"])

@matto_bot.on_message(filters.command(["sudolist", "sudoers", "sudo"]) & ~filters.private & filters.user([OWNER_ID, DevID]))
@language
async def list_sudo_users(client, message: Message, _):
    sm = await message.reply_text(_["sudo_5"])
    
    text = _["sudo_6"]
    count = 0
    
    for uid in SUDO_USERS:
        if uid == OWNER_ID:
            continue
        try:
            u = await matto_bot.get_users(uid)
            name = u.mention or u.first_name
            count += 1
            text += f"{count}➤ {name}\n"
        except:
            continue
            
    if count == 0:
        await sm.edit_text(_["sudo_7"])
    else:
        await sm.edit_text(text)

@matto_bot.on_message(filters.command("alldelsudo") & filters.user([OWNER_ID, DevID]))
async def delete_all_sudo_prompt(client, message: Message):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Verify Delete All", callback_data="wipe_all_sudo"),
            InlineKeyboardButton("Cancel", callback_data="cancel_wipe_sudo")
        ]
    ])
    await message.reply_text(
        "**⚠️ WARNING: SUDO WIPE**\n\n"
        "Are you sure you want to remove ALL sudo users? This cannot be undone.",
        reply_markup=keyboard
    )

@matto_bot.on_callback_query(filters.regex("wipe_all_sudo"))
async def execute_sudo_wipe(client, cb: CallbackQuery):
    if not check_owner(cb.from_user.id):
        return await cb.answer("Owner permissions required.", show_alert=True)
        
    removed = 0
    to_remove = [uid for uid in SUDO_USERS if uid != OWNER_ID]
    
    for uid in to_remove:
        if await remove_sudo(uid):
            SUDO_USERS.discard(uid)
            removed += 1
            
    await cb.edit_message_text(f"✅ Removed {removed} sudo users. Owner access retained.")

@matto_bot.on_callback_query(filters.regex("cancel_wipe_sudo"))
async def cancel_sudo_wipe(client, cb: CallbackQuery):
    await cb.edit_message_text("❌ Sudo wipe cancelled.")