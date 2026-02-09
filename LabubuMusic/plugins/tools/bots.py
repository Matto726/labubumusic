import asyncio
from pyrogram import filters, enums
from pyrogram.errors import FloodWait
from LabubuMusic import matto_bot

@matto_bot.on_message(filters.command("bots") & filters.group)
async def list_group_bots(client, message):
    chat = message.chat
    bot_list = []
    
    status_msg = await message.reply_text("Fetching bot list...")
    
    try:
        async for member in chat.get_members(filter=enums.ChatMembersFilter.BOTS):
            bot_list.append(member.user)
            
        if not bot_list:
            return await status_msg.edit_text("No bots found in this chat.")
            
        text_output = f"**🤖 Bot List for {chat.title}**\n\n"
        
        for bot in bot_list:
            text_output += f"🔸 @{bot.username}\n"
            
        text_output += f"\n**Total Bots:** {len(bot_list)}"
        
        await status_msg.edit_text(text_output)
        
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        await status_msg.edit_text(f"Error fetching bots: {e}")