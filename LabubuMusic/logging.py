import logging
import logging

# Configure logging format and handlers
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s : %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        logging.FileHandler("log.txt"),
        logging.StreamHandler(),
    ],
)

# Suppress noisy logs from external libraries
for lib in ["httpx", "pyrogram", "pytgcalls"]:
    logging.getLogger(lib).setLevel(logging.ERROR)

def log_factory(logger_name: str) -> logging.Logger:
    """Creates and returns a logger instance."""
    return logging.getLogger(logger_name)