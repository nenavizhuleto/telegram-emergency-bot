import logging
from telegram import Update

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def log_conv(update: Update, message: str):
    user = None 
    if not update.message:
        user = update.callback_query.from_user.username
    else:
        user = update.message.from_user.username

    if not user:
        user = "Unknown"

    logger.info(f"[{user}]: {message}")
