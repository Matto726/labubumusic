import sys
import traceback
from io import StringIO
from pyrogram import filters
from pyrogram.types import Message
from LabubuMusic import matto_bot
from config import OWNER_ID

async def async_executor(code_snippet, client, message):
    env = {
        "client": client,
        "message": message,
        "matto_bot": client,
    }
    
    func_def = "async def _exec(client, message):"
    indented_code = "\n".join(f"    {line}" for line in code_snippet.split("\n"))
    full_code = f"{func_def}\n{indented_code}"
    
    exec(full_code, env)
    return await env["_exec"](client, message)

@matto_bot.on_message(filters.command("eval") & filters.user(OWNER_ID))
async def eval_handler(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Give me some code to run.")
        
    code = message.text.split(None, 1)[1]
    
    status_msg = await message.reply_text("Running...")

    old_stdout = sys.stdout
    redirected_output = StringIO()
    sys.stdout = redirected_output
    
    try:
        await async_executor(code, client, message)
    except Exception:
        exc_traceback = traceback.format_exc()
        final_output = f"**Error:**\n`{exc_traceback}`"
    else:
        execution_output = redirected_output.getvalue()
        if not execution_output:
            execution_output = "Success (No Output)"
        final_output = f"**Output:**\n`{execution_output}`"
    finally:
        sys.stdout = old_stdout
        
    if len(final_output) > 4096:
        with open("eval_output.txt", "w") as f:
            f.write(final_output)
        await message.reply_document("eval_output.txt")
        await status_msg.delete()
    else:
        await status_msg.edit_text(final_output)