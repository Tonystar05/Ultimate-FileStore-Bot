#credit dena toh de ni dena toh mat de laadle ~ GPG
import logging
from logging.handlers import RotatingFileHandler
import os  # 🔥 NEW: Import os for environment variables

LOG_FILE_NAME = "bot.log"
PORT = '8000'
OWNER_ID = 821215952
MSG_EFFECT = 5046509860389126442

# BOT CONFIGURATION
# ===========================

# Telegram API Credentials (Get from https://my.telegram.org)
API_ID = 15529802
API_HASH = "92bcb6aa798a6f1feadbc917fccb54d3"
BOT_TOKEN = "8322793994:AAGiFwNq_MksA6K77RBSZ4bEpZSOT2IhFPA"

# ===========================
# DATABASE
# ===========================

# MongoDB Connection String
DATABASE_URI = "mongodb+srv://CineXeonFile:CineXeonFile@cluster0.dokar6b.mongodb.net/?appName=Cluster0"
DATABASE_NAME = "MovieSeries"

# ===========================
# CHANNELS
# ===========================

# Main Database Channel ID (where files are stored)
DB_CHANNEL = -1003536384063

# Force Subscribe Channels (users must join these)
FORCE_SUB_CHANNELS = []  # Example: [-1001234567890, -1009876543210]

# ===========================
# ADMIN
# ===========================

# Admin User IDs (can use admin commands)
ADMINS = [821215952]  # Example: [123456789, 987654321]

# ===========================
# SERVER (Optional)
# ===========================

# Use webhook instead of polling
WEBHOOK = False

# CUSTOMIZATION (Optional)
# ===========================

# Auto delete timer (seconds, 0 to disable)
AUTO_DELETE = 300

# Protect content (prevent forwarding)
PROTECT_CONTENT = False

# Disable share button
DISABLE_BUTTON = False


# VPLink URL Shortener Configuration
VPLINK_API_TOKEN = "akenamebepuresososebandhadhaga"
VPLINK_API_URL = "example.com"

# URL Shortener Providers Configuration
URL_SHORTENERS = {
    'vplink': {
        'name': 'VPLink',
        'api_url': 'https://vplink.in/api',
        'api_token': VPLINK_API_TOKEN,
        'format': 'text',
        'active': True
    }
}

# ===========================
# 🔥 NEW: STREAMING CONFIGURATION
# ===========================

# Enable/disable streaming feature
STREAM_MODE = True  # Set to False to disable streaming entirely

# Multi-client settings (for load balancing)
MULTI_CLIENT = False  # Set True if you want multiple bot tokens for streaming
SLEEP_THRESHOLD = 60  # Sleep threshold for multi-client mode
PING_INTERVAL = 1200  # 20 minutes - for keeping Heroku app alive

# Detect if running on Heroku
ON_HEROKU = 'DYNO' in os.environ

# Your domain for streaming links (REQUIRED for streaming to work)
# Replace with your actual domain (e.g., https://your-bot.onrender.com)
STREAM_URL = os.environ.get("STREAM_URL", "https://yourdomain.com")

# Streaming token expiry (in hours)
STREAM_TOKEN_EXPIRY = 24  # Default: 24 hours

def LOGGER(name: str, client_name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        f"[%(asctime)s - %(levelname)s] - {client_name} - %(name)s - %(message)s",
        datefmt='%d-%b-%y %H:%M:%S'
    )
    file_handler = RotatingFileHandler(LOG_FILE_NAME, maxBytes=50_000_000, backupCount=10)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
