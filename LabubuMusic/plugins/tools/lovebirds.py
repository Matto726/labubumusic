from pyrogram import filters
from LabubuMusic import matto_bot
from LabubuMusic.core.mongo import mongodb

users_col = mongodb.lovebirds_users
gifts_col = mongodb.lovebirds_gifts

GIFTS_MENU = {
    "🌹": {"name": "Rose", "cost": 10},
    "🍫": {"name": "Chocolate", "cost": 20},
    "💍": {"name": "Ring", "cost": 50},
    "💎": {"name": "Diamond", "cost": 100},
}

@matto_bot.on_message(filters.command(["top", "leaderboard"]))
async def show_leaderboard(client, message):
    try:
        top_users = await users_col.find().sort("coins", -1).limit(10).to_list(length=10)
        
        if not top_users:
            return await message.reply_text("📊 Leaderboard is empty!")
            
        text = "🏆 **Wealth Leaderboard**\n\n"
        medals = ["🥇", "🥈", "🥉"]
        
        for idx, user in enumerate(top_users):
            rank = medals[idx] if idx < 3 else f"#{idx+1}"
            uid = user.get("user_id")
            coins = user.get("coins", 0)
            text += f"{rank} 🆔 `{uid}` : {coins} 💰\n"
            
        await message.reply_text(text)
    except Exception as e:
        await message.reply_text(f"Error fetching leaderboard: {e}")
