import os
import shutil
import git
from pyrogram import filters
from LabubuMusic import matto_bot

def clone_and_compress(repo_url):
    name = repo_url.split("/")[-1].replace(".git", "")
    local_path = f"downloads/{name}"
    
    try:
        git.Repo.clone_from(repo_url, local_path)
        shutil.make_archive(local_path, 'zip', local_path)
        return f"{local_path}.zip"
    except Exception as e:
        print(f"Repo download error: {e}")
        return None
    finally:
        if os.path.exists(local_path):
            shutil.rmtree(local_path)

@matto_bot.on_message(filters.command("downloadrepo"))
async def git_download_cmd(client, message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: /downloadrepo [GitHub URL]")
        
    url = message.command[1]
    status = await message.reply_text("Downloading repository...")
    
    zip_file = clone_and_compress(url)
    
    if zip_file:
        await status.edit_text("Uploading zip...")
        await message.reply_document(zip_file)
        os.remove(zip_file)
        await status.delete()
    else:
        await status.edit_text("Failed to clone repository. Check visibility or URL.")