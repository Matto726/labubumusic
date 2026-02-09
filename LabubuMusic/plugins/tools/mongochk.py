import re
from pymongo import MongoClient
from pyrogram import filters
from LabubuMusic import matto_bot

MONGO_REGEX = re.compile(r"mongodb(?:\+srv)?:\/\/[^\s]+")

@matto_bot.on_message(filters.command("mongochk"))
async def check_mongo_connection(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /mongochk [MONGO_URL]")
        
    url = message.command[1]
    
    if not re.match(MONGO_REGEX, url):
        return await message.reply_text("❌ Invalid MongoDB URL format.")
        
    status_msg = await message.reply_text("🔄 Testing connection...")
    
    try:
        test_client = MongoClient(url, serverSelectionTimeoutMS=3000)
        test_client.server_info()
        await status_msg.edit_text("✅ **Connection Successful!**\n\nYour MongoDB URL is working.")
    except Exception as e:
        await status_msg.edit_text(f"❌ **Connection Failed**\n\nError: {e}")