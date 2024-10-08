from __future__ import annotations
from typing import Callable
import asyncio, multiprocessing
from datetime import datetime
from scripts.bot import TelegramBot, CommandProcessor
from db.db import DatabaseManager
from scripts.logger import Logger
from scripts.client import WebRequest
from scripts.scraper import ProductParser
from scripts.alert import AlertManager
from config.settings import MONITOR_PRODUCT_DELAY

# product monitor main async function. It envolves all the main class of the project
async def monitor_product(asin: str, client: Callable, parser: Callable, logger: Callable, processor: Callable, db: Callable, alert_manager: Callable) -> None:

    try:
 
        await asyncio.sleep(random.randint(0,5)
        
        html_response = await client.make_request(method = "GET", url = f"https://amazon.it/dp/{asin}") # GET request with WebRequest class, returns HTTPResponse dataclass
        product_data = await parser.parse_product_data(html_response) # parsing HTTPResponse's content with ProductParser class, returns Amazonproduct dataclass

        # Logging 

        if product_data.availability:
            logger.info(f"Object: {product_data.title} Status: Available Price: {product_data.current_price}€  Vendor: {product_data.vendor}  Rating: {product_data.rating}")
        else:
            logger.info(f"Object: {product_data.title} Status: Out Of Stock / No Offer  Price: N/A  Vendor: {product_data.vendor}  Rating: {product_data.rating}")
   

        # If the product is available, this block is assigned to notify all the user in the Database via Telegram or Email

        if product_data.availability:

            chat_ids = await db.notify_users(asin, product_data.current_price)
            chat_ids_list = [chat_id[0] for chat_id in chat_ids]
            email_list = list()

            for chat_id in chat_ids_list:

                email = await db.get_email_status(chat_id)

                if email != None:

                    email_list.append(email)

            # creating main message for the alerts using AmazonProduct attributes

            text = f"<b>{product_data.title}</b>\n\n🚀 Rating: {product_data.rating} {int(round(product_data.rating)) * '⭐️'}\n👤 Venditore: {product_data.vendor}\n⚙️ Status: Available ✅\n💰 Prezzo: <b>{product_data.current_price}€</b>\n\n🛒 <a href='{product_data.url}?tag=hwgrouptech0c-21'>Link al prodotto</a>"

            keyboard = {

                                 "inline_keyboard": [

                                                    [{"text": "Analytics 📈", "url" : f"https://it.camelcamelcamel.com/product/{asin}"}],
                                                    [{"text" : "Leggi le recensioni 🤩", "url" : f"https://amazon.it/product-reviews/{asin}?tag=hwgrouptech0c-21"}],
                                                        
                                                    ]                 

                        }
            
            # Sending Telegram inline_menu using CommandProcessor and TelegramBot classes

            for id in chat_ids_list:
                 
                 await processor.bot.send_menu(id, text, keyboard)
            
            # Sending email using AlertManager class

            for email in email_list:

                alert_manager.send_email_message(email, text)

            # Update last price in the db using DatabaseManager class
        
            await db.update_last_price(asin, product_data.current_price)
        
        else:

            await db.update_last_price(asin, 0.0)
        
        await db.update_title(asin, product_data.title)
        
    except Exception as e:
        logger.error(f"An error occurred while monitoring product at https://amazon.it/dp/{asin} : {str(e)}")

# Async functions assigned to run monitor_product function asyncronously
async def monitor_task(client: Callable, parser: Callable, logger: Callable, command_processor: Callable, db: Callable, alert_manager: Callable) -> None:

    while True:
        asin_list = await db.get_all_asins()
        tasks = [monitor_product(asin, client, parser, logger, command_processor, db, alert_manager) for asin in asin_list]
        await asyncio.gather(*tasks)
        await asyncio.sleep(MONITOR_PRODUCT_DELAY)

# Function assigned to define the process that enquiry Telegram for new updates and command from the users
def run_async_process1() -> None:

    logger = Logger(name = "TelegramUpdateListenerProcess").get_logger()
    db = DatabaseManager(logger)
    client = WebRequest(logger)
    command_processor = CommandProcessor(TelegramBot(client, logger), db)

    asyncio.run(command_processor.process_updates())     

# Function assigned to define the process that monitor products
def run_async_process2() -> None:

    logger = Logger(name = "ProductMonitorProcess").get_logger()
    db = DatabaseManager(logger)
    client = WebRequest(logger)
    parser = ProductParser(logger)
    command_processor = CommandProcessor(TelegramBot(client, logger), db)
    alert_manager = AlertManager(logger)

    asyncio.run(monitor_task(client, parser, logger, command_processor, db, alert_manager))

# Function assigned to create this two process
def main_task(logger: Callable) -> None:

    process1 = multiprocessing.Process(target = run_async_process1, name = 'TelegramUpdateListener')
    process2 = multiprocessing.Process(target = run_async_process2, name = 'ProductMonitor')
    
    process1.start()
    logger.info("Successfully created TelegramUpdateListener Process")
    process2.start()
    logger.info("Successfully created ProductMonitor Process")


def get_current_timestamp() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Function assigned to check if the Telegram API token is valid
async def check_telegram_bot_token(client: Callable, token: str) -> bool:

    response = await client.make_request("GET", url = f"https://api.telegram.org/bot{token}/getMe")
    data = response.request_content.json()

    if response.status_code == 200 and data['ok']:
        client.logger.info("Telegram API Token is valid ✓")
        return True
    else:
        client.logger.error("Telegram API Token is not valid or unconfigured, cannot start BOT Service ✗")
        return False

# Function assigned to check if the Telegram admin chat_id is valid
def check_telegram_admin_id(admin_chat_id: int, logger: Callable) -> bool:

    if admin_chat_id != 0:
        logger.info("Telegram Admin Chat ID is valid ✓")
        return True
    else:
        logger.error("Telegram Admin Chat ID is not valid or unconfigured, cannot start BOT Service ✗")
        return False
    
# Function assigned to check if the delay value is valid
def check_monitor_delay(logger: Callable) -> bool:

    if  MONITOR_PRODUCT_DELAY == 900:
        logger.info(f"Monitor delay value is valid but Default -> {MONITOR_PRODUCT_DELAY} seconds,  check .env configuration file ✓")
        return True
    elif MONITOR_PRODUCT_DELAY >= 0:
        logger.info(f"Monitor delay value is valid -> {MONITOR_PRODUCT_DELAY} seconds ✓")
        return True
    else:
        logger.error("Monitor delay value is unvalid, cannot start Product Monitor Service ✗")
        return False






