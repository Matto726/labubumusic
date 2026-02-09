import requests
from pyrogram import filters
from LabubuMusic import matto_bot

API_BASE = "https://api.truthordarebot.xyz/v1"

@matto_bot.on_message(filters.command("truth"))
async def fetch_truth(client, message):
    try:
        resp = requests.get(f"{API_BASE}/truth")
        if resp.status_code == 200:
            data = resp.json()
            question = data.get("question", "No question found.")
            await message.reply_text(f"🤔 **Truth:**\n\n{question}")
        else:
            await message.reply_text("API Error.")
    except:
        await message.reply_text("Failed to fetch truth.")

@matto_bot.on_message(filters.command("dare"))
async def fetch_dare(client, message):
    try:
        resp = requests.get(f"{API_BASE}/dare")
        if resp.status_code == 200:
            data = resp.json()
            task = data.get("question", "No dare found.")
            await message.reply_text(f"😈 **Dare:**\n\n{task}")
        else:
            await message.reply_text("API Error.")
    except:
        await message.reply_text("Failed to fetch dare.")