import os
import requests
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from LabubuMusic import matto_bot

def catbox_upload(file_path):
    api_url = "https://catbox.moe/user/api.php"
    payload = {"reqtype": "fileupload", "json": "true"}
    
    with open(file_path, "rb") as f:
        files = {"fileToUpload": f}
        resp = requests.post(api_url, data=payload, files=files)
        
    if resp.status_code == 200:
        return resp.text.strip()
    return None

@matto_bot.on_message(filters.command(["tgm", "upload", "catbox"]))
async def media_upload_handler(client, message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a photo or video to upload it.")
        
    status_msg = await message.reply_text("📥 Downloading media...")
    
    try:
        local_path = await message.reply_to_message.download()
        await status_msg.edit_text("📤 Uploading to Cloud...")
        
        link = catbox_upload(local_path)
        
        if link:
            btn = InlineKeyboardMarkup([[
                InlineKeyboardButton("🔗 View URL", url=link)
            ]])
            await status_msg.edit_text(
                f"✅ **Upload Successful!**\n\nLink: `{link}`",
                reply_markup=btn,
                disable_web_page_preview=True
            )
        else:
            await status_msg.edit_text("❌ Upload failed.")
            
    except Exception as e:
        await status_msg.edit_text(f"Error: {e}")
    finally:
        if 'local_path' in locals() and os.path.exists(local_path):
            os.remove(local_path)