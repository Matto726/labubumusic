import asyncio
import logging
from datetime import datetime
from pyrogram.enums import ChatType
from pytgcalls.exceptions import GroupCallNotFound

import config
from LabubuMusic import matto_bot
from LabubuMusic.core.call import Matto, auto_end_timers, call_counter
from LabubuMusic.misc import db
from LabubuMusic.utils.database import (
    get_client, set_loop, is_active_chat, 
    is_autoend, is_autoleave
)

async def chat_cleanup_task():
    """Periodically checks and leaves inactive chats."""
    while True:
        await asyncio.sleep(43200)
        
        from LabubuMusic.core.userbot import active_assistants
        
        if not await is_autoleave():
            continue
            
        for assistant_id in active_assistants:
            client = await get_client(assistant_id)
            leave_count = 0
            
            try:
                async for dialog in client.get_dialogs():
                    chat_type = dialog.chat.type
                    chat_id = dialog.chat.id
                    
                    if chat_type in [ChatType.SUPERGROUP, ChatType.GROUP, ChatType.CHANNEL]:
                        exempt_chats = [
                            config.LOG_GROUP_ID,
                            -1002169072536,
                            -1002499911479,
                            -1002252855734
                        ]
                        
                        if chat_id in exempt_chats:
                            continue
                            
                        if leave_count >= 20:
                            break
                            
                        if not await is_active_chat(chat_id):
                            try:
                                await client.leave_chat(chat_id)
                                leave_count += 1
                                logging.info(f"Auto-left chat: {chat_id}")
                            except Exception as e:
                                logging.error(f"Failed to leave {chat_id}: {e}")
            except Exception as e:
                logging.error(f"Auto-leave error: {e}")

async def stream_terminator():
    """Monitors active calls and ends empty streams."""
    while True:
        await asyncio.sleep(60)
        
        if not await is_autoend():
            continue

        tracked_chats = list(auto_end_timers.keys())
        removal_list = []
        
        for chat_id in tracked_chats:
            is_empty = False
            
            try:
                participants = await Matto.get_participants(chat_id)
                count = len(participants)
            except GroupCallNotFound:
                count = 1
                is_empty = True
            except Exception:
                count = 100
                
            if count <= 1:
                await set_loop(chat_id, 0)
                removal_list.append(chat_id)

                if chat_data := db.get(chat_id):
                    if msg := chat_data[0].get("mystic"):
                        try:
                            await msg.delete()
                        except:
                            pass

                try:
                    await Matto.stop_stream(chat_id)
                except:
                    pass

                if not is_empty:
                    try:
                        await matto_bot.send_message(
                            chat_id, 
                            "» Bot left the voice chat due to inactivity."
                        )
                    except:
                        pass

        for chat_id in removal_list:
            auto_end_timers.pop(chat_id, None)

asyncio.create_task(chat_cleanup_task())
asyncio.create_task(stream_terminator())