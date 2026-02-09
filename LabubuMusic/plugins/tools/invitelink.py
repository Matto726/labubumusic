import os
from pyrogram import filters
from LabubuMusic import matto_bot
from LabubuMusic.misc import SUDO_USERS

@matto_bot.on_message(filters.command("ginfo") & SUDO_USERS)
async def group_info_scraper(client, message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: /ginfo [GROUP_ID]")

    try:
        chat_id = int(message.command[1])
        chat = await client.get_chat(chat_id)

        try:
            link = chat.invite_link
            if not link:
                link = await client.export_chat_invite_link(chat_id)
        except:
            link = "Bot lacks permission to get link."

        report = [
            f"ID: {chat.id}",
            f"Title: {chat.title}",
            f"Username: @{chat.username}" if chat.username else "Username: None",
            f"Members: {chat.members_count}",
            f"Description: {chat.description or 'None'}",
            f"Scam: {chat.is_scam}",
            f"Fake: {chat.is_fake}",
            f"Link: {link}"
        ]

        filename = f"group_info_{chat_id}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(report))

        await message.reply_document(
            document=filename,
            caption=f"📊 Group Info for **{chat.title}**"
        )
        os.remove(filename)

    except ValueError:
        await message.reply_text("Invalid Chat ID format.")
    except Exception as e:
        await message.reply_text(f"Error fetching group info: {e}")