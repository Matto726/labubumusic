from pyrogram import filters
from pyrogram.raw.functions.phone import CreateGroupCall, DiscardGroupCall
from pyrogram.types import ChatPrivileges
from LabubuMusic import matto_bot
from LabubuMusic.core.call import Matto
from LabubuMusic.utils.database import get_assistant, set_loop
from LabubuMusic.utils.permissions import adminsOnly

@matto_bot.on_message(filters.command("startvc") & filters.group)
@adminsOnly("can_manage_video_chats")
async def start_voice_chat(client, message):
    chat_id = message.chat.id
    assistant = await get_assistant(chat_id)
    
    try:
        await assistant.invoke(
            CreateGroupCall(
                peer=await assistant.resolve_peer(chat_id),
                random_id=int(assistant.rnd_id()),
            )
        )
        await message.reply_text("✅ Voice Chat Started!")
    except Exception as e:
        await message.reply_text(f"Failed to start VC: {e}")

@matto_bot.on_message(filters.command("stopvc") & filters.group)
@adminsOnly("can_manage_video_chats")
async def stop_voice_chat(client, message):
    chat_id = message.chat.id
    assistant = await get_assistant(chat_id)
    
    try:
        calls = await assistant.get_group_call(chat_id) 
        await Matto.stop_stream_force(chat_id)
        await message.reply_text("✅ Voice Chat Ended!")
    except Exception as e:
        await message.reply_text(f"Could not stop VC. Make sure Assistant is admin.\nError: {e}")

@matto_bot.on_message(filters.video_chat_started & filters.group)
async def auto_vc_start_handler(_, message):
    await set_loop(message.chat.id, 0)
    await message.reply_text("📹 **Video Chat Started!**")