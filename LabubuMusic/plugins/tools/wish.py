import asyncio
import random
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import Message
from LabubuMusic import matto_bot

wish_sessions = {}

MORNING_QUOTES = [
    "🌞 <b>Wake up! It's a brand new day!</b> 🌼\n\n{mention}",
    "☕ <b>Grab your coffee, it's time to shine!</b>\n\n{mention}",
    "🌄 <b>New day, new opportunities! Good Morning!</b>\n\n{mention}",
    "🌻 <b>Rise and grind! Let's get this bread.</b>\n\n{mention}",
    "💫 <b>Sending you positive vibes this morning!</b>\n\n{mention}",
    "🌅 <b>The sun is up and so should you be!</b>\n\n{mention}",
    "🚀 <b>Let's make today amazing!</b>\n\n{mention}",
    "🧘 <b>Breathe in courage, breathe out fear. Good Morning!</b>\n\n{mention}",
    "🙏 <b>Namaste! Suprabhat! Aapka din mangalmay ho.</b> 🌺\n\n{mention}",
    "☕ <b>Chai piyo aur kaam pe lago! Good Morning!</b>\n\n{mention}",
    "🌞 <b>Nayi subah, nayi ummeed. Utho aur chha jao!</b>\n\n{mention}",
    "🍳 <b>Breakfast of champions time! Let's go!</b>\n\n{mention}",
    "🐦 <b>The early bird catches the worm. Wakey wakey!</b>\n\n{mention}",
    "💪 <b>Motivation level: 100%. Let's crush today.</b>\n\n{mention}",
    "🍵 <b>Adrak wali chai aur nayi shuruwat. Good Morning!</b>\n\n{mention}",
    "🌼 <b>Khush raho aur muskurate raho. Suprabhat!</b>\n\n{mention}",
    "🕰️ <b>Waqt kisi ka intezar nahi karta. Utho!</b>\n\n{mention}",
    "📅 <b>Today is a blank page. Write a good story.</b>\n\n{mention}",
    "🔔 <b>Uth jao! Sapne pure karne ka waqt ho gaya.</b>\n\n{mention}",
    "🔋 <b>Full charge? Let's get to work!</b>\n\n{mention}",
    "🌧️ <b>Weather forecast: 100% chance of success!</b>\n\n{mention}",
    "🛏️ <b>Chadar hatao, duniya hilaao! Good Morning!</b>\n\n{mention}",
]

AFTERNOON_QUOTES = [
    "🌞 <b>Good Afternoon! Halfway through the day!</b>\n\n{mention}",
    "🍱 <b>Hope you had a tasty lunch!</b>\n\n{mention}",
    "🥤 <b>Stay hydrated and keep going!</b>\n\n{mention}",
    "⚡ <b>Power through the afternoon slump!</b>\n\n{mention}",
    "🌇 <b>The sun is shining bright, just like you!</b>\n\n{mention}",
    "🚀 <b>Keep the momentum going! You got this.</b>\n\n{mention}",
    "🍦 <b>Time for a quick break? You deserve it.</b>\n\n{mention}",
    "🌞 <b>Shubh Dopahar! Thoda aaram bhi zaroori hai.</b>\n\n{mention}",
    "🍛 <b>Khana kha liya? Ab wapas focus karne ka time!</b>\n\n{mention}",
    "🔥 <b>Din aadha khatam, par josh pura hona chahiye!</b>\n\n{mention}",
    "🔋 <b>Recharge needed? Take a deep breath.</b>\n\n{mention}",
    "🐪 <b>It's Hump Day vibes (even if it's not Wednesday)!</b>\n\n{mention}",
    "🏖️ <b>Afternoon daydreaming allowed... for 5 minutes.</b>\n\n{mention}",
    "😴 <b>Aalsi mat bano, abhi toh shaam baaki hai!</b>\n\n{mention}",
    "☕ <b>Ek cup chai ho jaye? Good Afternoon!</b>\n\n{mention}",
    "🚧 <b>Rukna mana hai. Chalte raho!</b>\n\n{mention}",
    "🌵 <b>Stay sharp! The day isn't over yet.</b>\n\n{mention}",
    "🥪 <b>Don't work on an empty stomach. Eat something!</b>\n\n{mention}",
    "🥵 <b>Garmi hai, dimaag thanda rakho.</b>\n\n{mention}",
    "📉 <b>Don't let your energy crash. Push through!</b>\n\n{mention}",
    "⏳ <b>Shaam hone wali hai, kaam nipat lo jaldi.</b>\n\n{mention}",
]

NIGHT_QUOTES = [
    "🌙 <b>Good Night! Sweet dreams.</b> 😴\n\n{mention}",
    "⭐ <b>Time to recharge. Sleep tight!</b>\n\n{mention}",
    "🌌 <b>May the stars guide your dreams.</b>\n\n{mention}",
    "🛌 <b>Rest your head, tomorrow is a new day.</b>\n\n{mention}",
    "🦉 <b>Nighty night! See you tomorrow.</b>\n\n{mention}",
    "✨ <b>Look at the stars, look how they shine for you.</b>\n\n{mention}",
    "🔋 <b>Disconnect to reconnect. Good Night.</b>\n\n{mention}",
    "🛌 <b>Shubh Ratri! Kal ek nayi shuruwat hogi.</b>\n\n{mention}",
    "🌙 <b>So jao, duniya wahin rahegi. Good Night!</b>\n\n{mention}",
    "😴 <b>Aaram karo, sapne dekho. Shubh Ratri!</b>\n\n{mention}",
    "📵 <b>Put the phone away. Mental peace time.</b>\n\n{mention}",
    "🧸 <b>Sleep cozy, sleep sound.</b>\n\n{mention}",
    "🌑 <b>Darkness is just a canvas for your dreams.</b>\n\n{mention}",
    "🧘 <b>Din bhar ki thakan bhool jao. Shubh Ratri.</b>\n\n{mention}",
    "🌠 <b>Sapno ki duniya mein kho jao. Good Night!</b>\n\n{mention}",
    "💤 <b>Chinta chodo, bistar pakdo. So jao!</b>\n\n{mention}",
    "🥱 <b>Yawning is your body screaming for bed. Go!</b>\n\n{mention}",
    "🔇 <b>Silence the noise. Listen to the peace. GN!</b>\n\n{mention}",
    "🌝 <b>Chand nikal aaya hai, ab tum so jao.</b>\n\n{mention}",
    "💭 <b>Raat ka sukoon sabse pyaara hota hai. Enjoy it.</b>\n\n{mention}",
    "🔌 <b>Switching off mode... System Shutdown.</b>\n\n{mention}",
    "🦁 <b>Sher bhi sota hai. Tum bhi so jao.</b>\n\n{mention}",
]

async def run_wish_loop(client, chat_id, messages_list):
    """Generic loop to handle tagging."""
    if chat_id in wish_sessions:
        return
    
    wish_sessions[chat_id] = True
    
    try:
        async for member in client.get_chat_members(chat_id):
            if chat_id not in wish_sessions:
                break
                
            if member.user.is_bot or member.user.is_deleted:
                continue
                
            text = random.choice(messages_list).format(mention=member.user.mention)
            
            try:
                await client.send_message(chat_id, text)
            except Exception:
                pass

            await asyncio.sleep(3)
            
    finally:
        wish_sessions.pop(chat_id, None)

@matto_bot.on_message(filters.command(["gmtag", "goodmorning"]) & filters.group)
async def trigger_morning(client, message: Message):
    if message.chat.id in wish_sessions:
        return await message.reply_text("⏳ A wish session is already active.")
    await message.reply_text("🌞 <b>Starting Good Morning wishes!</b>")
    await run_wish_loop(client, message.chat.id, MORNING_QUOTES)

@matto_bot.on_message(filters.command(["gatag", "goodafternoon"]) & filters.group)
async def trigger_afternoon(client, message: Message):
    if message.chat.id in wish_sessions:
        return await message.reply_text("⏳ A wish session is already active.")
    await message.reply_text("🌤 <b>Starting Good Afternoon wishes!</b>")
    await run_wish_loop(client, message.chat.id, AFTERNOON_QUOTES)

@matto_bot.on_message(filters.command(["gntag", "goodnight"]) & filters.group)
async def trigger_night(client, message: Message):
    if message.chat.id in wish_sessions:
        return await message.reply_text("⏳ A wish session is already active.")
    await message.reply_text("🌙 <b>Starting Good Night wishes!</b>")
    await run_wish_loop(client, message.chat.id, NIGHT_QUOTES)

@matto_bot.on_message(filters.command(["stopall", "stopwishes"]) & filters.group)
async def stop_wishes(client, message: Message):
    if message.chat.id in wish_sessions:
        del wish_sessions[message.chat.id]
        await message.reply_text("🛑 <b>Wish tagging stopped successfully.</b>")
    else:
        await message.reply_text("❌ <b>No active wish session found.</b>")

@matto_bot.on_message(filters.command("taghelp") & filters.group)
async def wish_help_menu(client, message: Message):
    help_msg = (
        "🏷️ <b>Wish Tagging Commands</b>\n\n"
        "<b>Morning:</b> `/gmtag`\n"
        "<b>Afternoon:</b> `/gatag`\n"
        "<b>Night:</b> `/gntag`\n\n"
        "<b>Control:</b> `/stopall` - Stop the current tagging loop.\n\n"
        "<i>Note: Tags one user every 3 seconds to avoid flood limits.</i>"
    )
    await message.reply_text(help_msg)