import os
from distutils.util import strtobool

from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

MONITOR_PRODUCT_DELAY = int(os.getenv("MONITOR_PRODUCT_DELAY", "900"))

# Telegram Alert settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "0")  # use @BotFather on Telegram
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

# Email Alert settings
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.example.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))  # Convert to int, default to 587
EMAIL_USE_TLS = strtobool(os.getenv("EMAIL_USE_TLS", "true"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "sender@example.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "password")

SAVE_LOGS_TO_FILE = strtobool(os.getenv("SAVE_LOGS_TO_FILE", "true"))


# Config Path
config_path= f"{os.getcwd()}/config/"
