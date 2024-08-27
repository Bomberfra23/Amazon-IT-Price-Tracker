import concurrent.futures
import datetime
import logging
import os
import time

from config import settings
from scripts.GUI import logo
from scripts.functions import (
    task,
    read_data,
    urls,
    price_targets,
    telegram_alerts_settings,
    email_alerts_settings,
    get_delay_input,
    get_threads_input,
    check_telegram_alert,
    check_email_alert
)

formats = "[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s"

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
    print(logo)
    input("Press ENTER to starting configuration and reading data")
    read_data()
    number_of_threads = get_threads_input()
    tasks_delay = get_delay_input()
    check_telegram_alert()
    check_email_alert()
    input("Press ENTER to starting monitoring products")
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"Action: Ready!")

    while True:
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_threads) as executor:
            executor.map(task, urls, price_targets, telegram_alerts_settings, email_alerts_settings)
            # parallelize product tasks using lists/dicts object as args
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"Tasks completed in: {int(time.time() - start_time)}")
        time.sleep(tasks_delay)  # delay between tasks


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Exiting...")
        exit()
