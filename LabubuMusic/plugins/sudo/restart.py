import asyncio
import os
import shutil
import socket
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from pyrogram import filters
import config
from LabubuMusic import matto_bot
from LabubuMusic.misc import SUDO_USERS
from LabubuMusic.utils.database import (
    get_active_chats, remove_active_chat, remove_active_video_chat
)
from LabubuMusic.utils.decorators.language import language
from LabubuMusic.utils.pastebin import NandBin

@matto_bot.on_message(filters.command(["getlog", "logs", "getlogs"]) & SUDO_USERS)
@language
async def log_fetcher(client, message, _):
    try:
        if os.path.exists("log.txt"):
            await message.reply_document(document="log.txt")
        else:
            await message.reply_text("Log file not found.")
    except Exception as e:
        await message.reply_text(f"Error sending logs: {e}")

@matto_bot.on_message(filters.command(["update", "gitpull"]) & SUDO_USERS)
@language
async def updater_func(client, message, _):
    status_msg = await message.reply_text(_["server_1"])
    
    try:
        repo = Repo()
    except (InvalidGitRepositoryError, GitCommandError):
        repo = Repo.init()
        try:
            origin = repo.create_remote("origin", config.UPSTREAM_REPO)
            origin.fetch()
            repo.create_head("master", origin.refs.master)
            repo.heads.master.set_tracking_branch(origin.refs.master)
            repo.heads.master.checkout(True)
        except Exception:
            return await status_msg.edit(_["server_2"])

    try:
        origin = repo.remote("origin")
        origin.fetch()
        await status_msg.edit(_["server_3"])

        if repo.rev_parse("HEAD") == repo.rev_parse("origin/master"):
            return await status_msg.edit(_["server_4"])
            
        repo.git.reset("--hard", "FETCH_HEAD")

        await status_msg.edit(_["server_5"])
        os.system("pip3 install -r requirements.txt")
        
        await status_msg.edit(_["server_6"])

        os.system(f"kill -9 {os.getpid()} && bash start")
        exit()
        
    except Exception as e:
        await status_msg.edit(_["server_10"].format(e))

@matto_bot.on_message(filters.command(["restart", "reboot"]) & SUDO_USERS)
async def reboot_handler(client, message):
    msg = await message.reply_text("System Rebooting...")

    active_chats = await get_active_chats()
    for cid in active_chats:
        try:
            await matto_bot.send_message(
                int(cid), 
                "**Bot is restarting for maintenance.**\nWe will be back in 30 seconds."
            )
            await remove_active_chat(cid)
            await remove_active_video_chat(cid)
        except:
            pass

    for folder in ["downloads", "cache", "raw_files"]:
        try:
            if os.path.exists(folder):
                shutil.rmtree(folder)
        except:
            pass
            
    await msg.edit("Restarting Process Initiated.")
    os.system(f"kill -9 {os.getpid()} && bash start")
    exit()