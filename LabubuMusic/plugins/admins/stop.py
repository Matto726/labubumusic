from pyrogram import filters, types
from LabubuMusic import matto_bot
from LabubuMusic.core.call import Matto
from LabubuMusic.utils.database import set_loop
from LabubuMusic.utils.decorators import AdminRightsCheck
from LabubuMusic.utils.inline import close_markup
from config import BANNED_USERS

@matto_bot.on_message(filters.command(["end", "stop", "cend", "cstop"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def end_stream_cmd(client, message: types.Message, _, chat_id):
    if len(message.command) != 1:
        return
        
    await Matto.stop_stream(chat_id)
    await set_loop(chat_id, 0)
    
    await message.reply_text(
        _["admin_5"].format(message.from_user.mention),
        reply_markup=close_markup(_)
    )