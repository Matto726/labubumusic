from pyrogram import filters
from pyrogram.types import Message
from LabubuMusic import matto_bot
from LabubuMusic.utils.database import get_loop, set_loop
from LabubuMusic.utils.decorators import AdminRightsCheck
from LabubuMusic.utils.inline import close_markup
from config import BANNED_USERS

@matto_bot.on_message(filters.command(["loop", "cloop"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def loop_manager(client, message: Message, _, chat_id):
    if len(message.command) != 2:
        return await message.reply_text(_["admin_17"])

    arg = message.text.split(None, 1)[1].strip()
    user_mention = message.from_user.mention

    if arg.isdigit():
        count = int(arg)
        if 1 <= count <= 10:
            current_loop = await get_loop(chat_id)
            new_val = min(current_loop + count, 10) if current_loop != 0 else count
            
            await set_loop(chat_id, new_val)
            return await message.reply_text(
                text=_["admin_18"].format(new_val, user_mention),
                reply_markup=close_markup(_),
            )
        else:
            return await message.reply_text(_["admin_17"])

    elif arg.lower() == "enable":
        await set_loop(chat_id, 10)
        return await message.reply_text(
            text=_["admin_18"].format("Enabled", user_mention),
            reply_markup=close_markup(_),
        )

    elif arg.lower() == "disable":
        await set_loop(chat_id, 0)
        return await message.reply_text(
            _["admin_19"].format(user_mention),
            reply_markup=close_markup(_),
        )
    else:
        return await message.reply_text(_["admin_17"])