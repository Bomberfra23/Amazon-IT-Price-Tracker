import os
from distutils.util import strtobool

from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Telegram Alert settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # use @BotFather on Telegram
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "123456")  # Default to "123456" if not set
SAVE_LOGS_TO_FILE = strtobool(os.getenv("SAVE_LOGS_TO_FILE", "false"))

# Email Alert settings
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.example.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))  # Convert to int, default to 587
EMAIL_USE_TLS = strtobool(os.getenv("EMAIL_USE_TLS", "true"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "sender@example.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "password")
EMAIL_ADDRESSEE = os.getenv("EMAIL_ADDRESSEE", "addressee@example.com")


# Config Path
config_path= f"{os.getcwd()}/config/"
