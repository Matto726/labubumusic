from motor.motor_asyncio import AsyncIOMotorClient
import certifi
from config import MONGO_DB_URI
from ..logging import log_factory

log_factory("LabubuMusic").info("Initializing Mongo Database...")

try:
    # We use certifi to provide a valid CA bundle for the SSL handshake
    _client = AsyncIOMotorClient(
        MONGO_DB_URI, 
        tlsCAFile=certifi.where()
    )
    
    # Keeping DB name as 'Yukki' to preserve data if migrating
    mongodb = _client.Yukki
    log_factory("LabubuMusic").info("Mongo Database Connected.")
except Exception as e:
    log_factory("LabubuMusic").error(f"Mongo Connection Failed: {e}")
    exit()
