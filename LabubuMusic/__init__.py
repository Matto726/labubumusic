from LabubuMusic.core.bot import Matto
from LabubuMusic.core.dir import dirr
from LabubuMusic.core.git import git
from LabubuMusic.core.userbot import Userbot
from LabubuMusic.misc import initialize_database, connect_heroku
from .logging import log_factory
from .platforms import (
    AppleAPI, CarbonAPI, SoundAPI, SpotifyAPI, 
    RessoAPI, TeleAPI, YouTubeAPI
)

# Initialize System Dependencies
dirr()
git()
initialize_database()
connect_heroku()

# Initialize Bot Clients
matto_bot = Matto()
userbot = Userbot()

# Initialize Music Platforms
Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()