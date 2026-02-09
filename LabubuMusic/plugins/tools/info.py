import os
import re
from pyrogram import filters, types, enums
from LabubuMusic import matto_bot

def get_user_status(status):
    status_map = {
        enums.UserStatus.RECENTLY: "Recently Active",
        enums.UserStatus.LAST_WEEK: "Last Week",
        enums.UserStatus.LONG_AGO: "Long Time Ago",
        enums.UserStatus.OFFLINE: "Offline",
        enums.UserStatus.ONLINE: "Online"
    }
    return status_map.get(status, "Unknown")

@matto_bot.on_message(filters.command(["info", "userinfo"]))
async def user_info_fetcher(client, message):
    target = None

    if len(message.command) == 2:
        try:
            target = await client.get_users(message.command[1])
        except Exception:
            return await message.reply_text("❌ User not found.")
    elif message.reply_to_message:
        target = message.reply_to_message.from_user
    else:
        target = message.from_user

    if not target:
        return await message.reply_text("❌ Could not identify user.")

    status_text = get_user_status(target.status)
    dc_id = target.dc_id or "Unknown"
    is_premium = "✅ Yes" if target.is_premium else "❌ No"
    username = f"@{target.username}" if target.username else "No Username"

    try:
        full_user = await client.get_chat(target.id)
        bio = full_user.bio or "No Bio Set"
    except:
        bio = "Unavailable"

    photo_id = full_user.photo.big_file_id if full_user.photo else None
    
    info_caption = (
        f"👤 **User Information**\n\n"
        f"🆔 **ID:** `{target.id}`\n"
        f"👤 **Name:** {target.first_name}\n"
        f"🔗 **Username:** {username}\n"
        f"💎 **Premium:** {is_premium}\n"
        f"📡 **DC ID:** {dc_id}\n"
        f"🔋 **Status:** {status_text}\n"
        f"📝 **Bio:** {bio}"
    )
    
    buttons = types.InlineKeyboardMarkup([
        [types.InlineKeyboardButton("🔗 Profile Link", url=f"tg://user?id={target.id}")]
    ])

    if photo_id:
        await message.reply_photo(photo_id, caption=info_caption, reply_markup=buttons)
    else:
        await message.reply_text(info_caption, reply_markup=buttons)