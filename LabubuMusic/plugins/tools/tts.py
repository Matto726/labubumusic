import io
import os
from gtts import gTTS
from pyrogram import filters
from LabubuMusic import matto_bot

@matto_bot.on_message(filters.command("tts"))
async def text_to_audio(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /tts [text]")
        
    text_content = message.text.split(None, 1)[1]
    
    try:
        tts_obj = gTTS(text=text_content, lang='hi')
        audio_stream = io.BytesIO()
        tts_obj.write_to_fp(audio_stream)
        audio_stream.seek(0)
        audio_stream.name = "speech.mp3"
        
        await message.reply_audio(audio_stream)
        
    except Exception as e:
        await message.reply_text(f"TTS Error: {e}")