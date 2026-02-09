from pyrogram import filters
from LabubuMusic import matto_bot

class FontStyles:
    @staticmethod
    def typewriter(text):
        mapping = str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣")
        return text.translate(mapping)

    @staticmethod
    def outline(text):
        mapping = str.maketrans("abcdefghijklmnopqrstuvwxyz", "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫")
        return text.translate(mapping)
    

@matto_bot.on_message(filters.command("font"))
async def font_convert_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /font [text]")
        
    text = message.text.split(None, 1)[1]
    
    styled_text = FontStyles.typewriter(text)
    
    await message.reply_text(f"Typewriter: `{styled_text}`")
