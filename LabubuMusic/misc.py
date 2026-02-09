import socket
import time
import heroku3
from pyrogram import filters
import config
from LabubuMusic.core.mongo import mongodb
from .logging import log_factory

SUDO_USERS = filters.user()
HEROKU_APP = None
BOOT_TIMESTAMP = time.time()

def check_heroku_env():
    """Checks if the bot is running on Heroku."""
    return "heroku" in socket.getfqdn()

HEROKU_CONFIG = [
    "/", "@", ".", "com", ":", "git", "heroku", "push",
    str(config.HEROKU_API_KEY), "https", str(config.HEROKU_APP_NAME),
    "HEAD", "master",
]

def initialize_database():
    global db
    db = {}
    log_factory(__name__).info("Local Database Initialized.")

async def load_sudo_users():
    global SUDO_USERS
    SUDO_USERS.add(config.OWNER_ID)
    
    sudo_collection = mongodb.sudoers
    sudo_data = await sudo_collection.find_one({"sudo": "sudo"})
    
    current_sudoers = sudo_data["sudoers"] if sudo_data else []
    
    # Ensure owner is in sudoers
    if config.OWNER_ID not in current_sudoers:
        current_sudoers.append(config.OWNER_ID)
        await sudo_collection.update_one(
            {"sudo": "sudo"},
            {"$set": {"sudoers": current_sudoers}},
            upsert=True,
        )
    
    if current_sudoers:
        for user_id in current_sudoers:
            SUDO_USERS.add(user_id)
            
    log_factory(__name__).info("Sudoers Loaded Successfully.")

def connect_heroku():
    global HEROKU_APP
    if check_heroku_env():
        if config.HEROKU_API_KEY and config.HEROKU_APP_NAME:
            try:
                heroku_conn = heroku3.from_key(config.HEROKU_API_KEY)
                HEROKU_APP = heroku_conn.app(config.HEROKU_APP_NAME)
                log_factory(__name__).info("Heroku App Configured.")
            except BaseException:
                log_factory(__name__).warning(
                    "Heroku configuration failed. Check API Key and App Name."
                )