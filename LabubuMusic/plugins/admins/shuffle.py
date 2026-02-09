import random
from pyrogram import filters, types
from LabubuMusic import matto_bot
from LabubuMusic.misc import db
from LabubuMusic.utils.decorators import AdminRightsCheck
from LabubuMusic.utils.inline import close_markup
from config import BANNED_USERS

@matto_bot.on_message(filters.command(["shuffle", "cshuffle"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def shuffle_queue(client, message: types.Message, _, chat_id):
    queue = db.get(chat_id)
    if not queue:
        return await message.reply_text(_["queue_2"])

    try:
        current_track = queue.pop(0)
    except IndexError:
         return await message.reply_text(_["admin_15"], reply_markup=close_markup(_))

    if not queue:
        queue.insert(0, current_track)
        return await message.reply_text(_["admin_15"], reply_markup=close_markup(_))

    random.shuffle(queue)
    queue.insert(0, current_track)
    
    await message.reply_text(
        _["admin_16"].format(message.from_user.mention),
        reply_markup=close_markup(_)
    )