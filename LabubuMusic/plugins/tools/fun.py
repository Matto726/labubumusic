import requests
from pyrogram import filters
from pyrogram.types import Message
from LabubuMusic import matto_bot

GAMES_EMOJI = {
    "dice": "🎲",
    "ludo": "🎲",
    "dart": "🎯",
    "basket": "🏀",
    "basketball": "🏀",
    "football": "⚽",
    "slot": "🎰",
    "bowling": "🎳",
    "jackpot": "🎰"
}

@matto_bot.on_message(filters.command(list(GAMES_EMOJI.keys())))
async def play_games(client, message: Message):
    cmd = message.command[0].lower()
    emoji = GAMES_EMOJI.get(cmd)
    
    if emoji:
        result = await client.send_dice(message.chat.id, emoji=emoji)
        await message.reply_text(f"You scored: **{result.dice.value}**")

BORED_API = "https://apis.scrimba.com/bored/api/activity"

@matto_bot.on_message(filters.command("bored"))
async def boredom_killer(client, message: Message):
    try:
        res = requests.get(BORED_API)
        if res.status_code == 200:
            content = res.json()
            activity = content.get("activity")
            if activity:
                return await message.reply_text(f"🥱 **Bored? Try this:**\n\n✨ {activity}")
    except Exception:
        pass
    
    await message.reply_text("I couldn't find anything fun to do right now.")