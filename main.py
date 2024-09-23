import asyncio
from scripts.GUI import generate_logo

from scripts.functions import (

    main_task, check_telegram_admin_id, 
    check_telegram_bot_token, 
    check_monitor_delay
    
    )

from scripts.logger import Logger
from scripts.alert import AlertManager
from scripts.bot import TelegramBot
from scripts.client import WebRequest
from db.db import DatabaseManager

# Call main classes for the main process

logger = Logger().get_logger()
client = WebRequest(logger)
alert_manager = AlertManager(logger)
telegram_bot = TelegramBot(client, logger)
db = DatabaseManager(logger)


__version__ = 'BETA V0.1.0'


def main():
    print(generate_logo(__version__, "Franco Pisani"))
    input("Press any key to check credentials and configuration before starting...")

    # Check of the .env setup and credentials. If one is not valid, the program flow terminates

    if not asyncio.run(check_telegram_bot_token(client, telegram_bot.token)):
        exit(0)
    elif not check_telegram_admin_id(telegram_bot.admin, logger):
        exit(0)
    elif not check_monitor_delay(logger):
        exit(0)
    elif not alert_manager.verify_server_configuration():
        exit(0)

    input("Press any key to start monitoring product service and telegram bot service...")

    # Run Asynchronous DatabaseManager class method to create db if doesn't exist

    asyncio.run(db.create_tables())
    main_task(logger)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)
