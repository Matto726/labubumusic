import os
from PIL import Image, ImageDraw, ImageFont, ImageChops
from pyrogram import filters
from LabubuMusic import matto_bot
from logging import getLogger

LOGGER = getLogger(__name__)

welcome_cache = {}

def make_circle(img):
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + img.size, fill=255)
    
    result = Image.new("RGBA", img.size, (0, 0, 0, 0))
    result.paste(img, (0, 0), mask=mask)
    return result

def generate_welcome_image(profile_pic_path, name, chat_title, user_id):
    bg_path = "LabubuMusic/assets/welcome_bg.png" 
    font_path = "LabubuMusic/assets/font.ttf"

    background = Image.open(bg_path).convert("RGBA")
    draw = ImageDraw.Draw(background)

    try:
        font_large = ImageFont.truetype(font_path, 60)
        font_small = ImageFont.truetype(font_path, 40)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((500, 200), f"Welcome {name}", fill="white", font=font_large)
    draw.text((500, 300), f"To: {chat_title}", fill="white", font=font_small)
    draw.text((500, 380), f"ID: {user_id}", fill="white", font=font_small)

    if profile_pic_path:
        pfp = Image.open(profile_pic_path).convert("RGBA")
        pfp = pfp.resize((400, 400))
        pfp = make_circle(pfp)
        background.paste(pfp, (50, 150), pfp)

    output_path = f"cache/welcome_{user_id}.png"
    background.save(output_path)
    return output_path

@matto_bot.on_message(filters.new_chat_members, group=1)
async def welcome_handler(client, message):
    for user in message.new_chat_members:
        if user.is_bot:
            continue

        prev_msg = welcome_cache.get(message.chat.id)
        if prev_msg:
            try:
                await prev_msg.delete()
            except:
                pass

        try:
            if user.photo:
                pfp_path = await client.download_media(user.photo.big_file_id)
            else:
                pfp_path = None

            img_path = await asyncio.get_event_loop().run_in_executor(
                None, 
                generate_welcome_image, 
                pfp_path, 
                user.first_name, 
                message.chat.title, 
                user.id
            )

            sent_msg = await message.reply_photo(
                photo=img_path,
                caption=f"Welcome {user.mention} to {message.chat.title}!"
            )
            
            welcome_cache[message.chat.id] = sent_msg

            if pfp_path and os.path.exists(pfp_path):
                os.remove(pfp_path)
            if os.path.exists(img_path):
                os.remove(img_path)
                
        except Exception as e:
            LOGGER.error(f"Welcome Error: {e}")