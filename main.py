import concurrent.futures
import logging
import os
import time

from config import settings
from scripts.GUI import generate_logo
from scripts.functions import (
    task,
    read_data,
    get_delay_input,
    get_threads_input,
    urls,
    price_targets,
    telegram_alerts_settings,
    email_alerts_settings,
    save_user_inputs,
    load_user_inputs,
    check_telegram_alert,
    check_email_alert
)

__version__ = 'ALPHA V0.0.2'

formats = "[%(levelname) 4s/%(asctime)s] %(name)s: %(message)s"

logger = logging.getLogger("AmazonPriceTracker")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(formats))
logger.addHandler(console_handler)

if settings.SAVE_LOGS_TO_FILE:
    file_handler = logging.FileHandler(f"{os.getcwd()}/logs.log")
    file_handler.setFormatter(logging.Formatter(formats))
    logger.addHandler(file_handler)

logging.getLogger().setLevel(logging.ERROR)


# main functions contains the main menu and thread's pool
def main():
    print(generate_logo(__version__, "Franco Pisani"))
    input("Press ENTER to starting configuration and reading data")
    read_data()

    number_of_threads, tasks_delay, telegram_check, email_check = load_user_inputs()

    if number_of_threads is None or tasks_delay is None:
        number_of_threads = get_threads_input()
        tasks_delay = get_delay_input()

        telegram_check = check_telegram_alert()
        email_check = check_email_alert()

        save_user_inputs(number_of_threads, tasks_delay, telegram_check, email_check)
    else:
        if telegram_check:
            logger.info("Telegram Alert was previously checked and verified.")
        if email_check:
            logger.info("Email Alert was previously checked and verified.")

    input("Press ENTER to starting monitoring products")
    logger.info(f"Action: Ready!")

    while True:
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_threads) as executor:
            executor.map(task, urls, price_targets, telegram_alerts_settings, email_alerts_settings)
            # parallelize product tasks using lists/dicts object as args
        logger.info(f"Tasks completed in: {int(time.time() - start_time)}")
        time.sleep(tasks_delay)  # delay between tasks


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Exiting...")
        exit(0)
