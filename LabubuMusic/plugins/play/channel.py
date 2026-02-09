from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus, ChatType
from pyrogram.types import Message

from LabubuMusic import matto_bot
from LabubuMusic.utils.database import set_cmode
from LabubuMusic.utils.decorators.admins import AdminActual
from config import BANNED_USERS

@matto_bot.on_message(filters.command(["channelplay"]) & filters.group & ~BANNED_USERS)
@AdminActual
async def channel_play_toggle(client, message: Message, _):

    if len(message.command) < 2:
        return await message.reply_text(_["cplay_1"].format(message.chat.title))

    cmd_arg = message.text.split(None, 2)[1].lower().strip()

    if cmd_arg == "disable":
        await set_cmode(message.chat.id, None)
        return await message.reply_text(_["cplay_7"])

    elif cmd_arg == "linked":
        chat_info = await matto_bot.get_chat(message.chat.id)
        if chat_info.linked_chat:
            target_chat_id = chat_info.linked_chat.id
            await set_cmode(message.chat.id, target_chat_id)
            return await message.reply_text(
                _["cplay_3"].format(chat_info.linked_chat.title, target_chat_id)
            )
        else:
            return await message.reply_text(_["cplay_2"])

    else:
        try:
            target_chat = await matto_bot.get_chat(cmd_arg)
        except:
            return await message.reply_text(_["cplay_4"])

        if target_chat.type != ChatType.CHANNEL:
            return await message.reply_text(_["cplay_5"])

        try:
            creator_found = False
            async for member in matto_bot.get_chat_members(
                target_chat.id, filter=ChatMembersFilter.ADMINISTRATORS
            ):
                if member.status == ChatMemberStatus.OWNER:
                    creator_username = member.user.username
                    creator_id = member.user.id
                    creator_found = True
                    break
            
            if not creator_found:
                 return await message.reply_text(_["cplay_4"])

        except:
            return await message.reply_text(_["cplay_4"])

        if creator_id != message.from_user.id:
            return await message.reply_text(_["cplay_6"].format(target_chat.title, creator_username))

        await set_cmode(message.chat.id, target_chat.id)
        return await message.reply_text(_["cplay_3"].format(target_chat.title, target_chat.id))