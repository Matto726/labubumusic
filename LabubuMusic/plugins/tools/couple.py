from datetime import datetime, timedelta
import pytz
import random
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from LabubuMusic import matto_bot
from LabubuMusic.utils import get_image, save_couple

def get_current_date():
    tz = pytz.timezone("Asia/Kolkata")
    return datetime.now(tz).strftime("%d/%m/%Y")

def get_next_date():
    tz = pytz.timezone("Asia/Kolkata")
    return (datetime.now(tz) + timedelta(days=1)).strftime("%d/%m/%Y")

@matto_bot.on_message(filters.command(["couple", "couples"]))
async def couple_selector(client, message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command is for groups only.")
        
    chat_id = message.chat.id
    today_str = get_current_date()
    
    try:
        members_list = []
        async for m in client.get_chat_members(chat_id, limit=100):
            if not m.user.is_bot:
                members_list.append(m.user.id)
                
        if len(members_list) < 2:
            return await message.reply_text("Not enough members to form a couple!")
            
        c1_id = random.choice(members_list)
        members_list.remove(c1_id)
        c2_id = random.choice(members_list)
        
        user1 = await client.get_users(c1_id)
        user2 = await client.get_users(c2_id)
        
        text_result = (
            f"💘 **Couple of the Day** 💘\n\n"
            f"💞 {user1.mention} + {user2.mention} = 💖\n\n"
            f"Next selection on {get_next_date()}"
        )

        btn = InlineKeyboardMarkup([[
            InlineKeyboardButton("Add Me", url=f"https://t.me/{matto_bot.username}?startgroup=true")
        ]])
        
        await message.reply_text(text_result, reply_markup=btn)
        
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")