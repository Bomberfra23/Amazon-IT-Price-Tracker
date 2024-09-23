import asyncio, re
from urllib.parse import urlparse
from typing import Callable
from config.settings import (
    TELEGRAM_BOT_TOKEN,
    ADMIN_CHAT_ID
)

# Dict used to store temporary user states 

user_states = dict()

# Telegram Bot main class that contains all the functions assigned to communicate with the API
class TelegramBot:
    
    __slots__ = ("token", "admin", "base_url", "client", "logger")

    def __init__(self, client: Callable, logger: Callable):
       
       self.token = TELEGRAM_BOT_TOKEN
       self.admin = ADMIN_CHAT_ID
       self.base_url = f"https://api.telegram.org/bot{self.token}" 
       self.client = client
       self.logger = logger

    async def send_message(self, chat_id: int, text: str) -> None:

      try:

        url: str = f"{self.base_url}/sendMessage"

        payload = {

            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }

        await self.client.make_request(method="POST", url=url, json=payload)
        self.logger.info(f"Action: Telegram message sent! to {chat_id}")

      except Exception as e:   
        self.logger.error(f"Error: Unable to send Telegram message to {chat_id}!: {e}")
    
    async def edit_message(self, chat_id: int, message_id: int, new_text: str) -> None:

        try:

            url: str = f"{self.base_url}/editMessageText"

            payload = {

                'chat_id' : chat_id,
                'message_id' : message_id,
                'text': new_text,
                'parse_mode': 'HTML'

            }

            await self.client.make_request(method="POST", url=url, json=payload)
            self.logger.info(f"Action: Telegram message edit! to {chat_id}")

        except Exception as e:   
            self.logger.error(f"Error: Unable to send Telegram message to {chat_id}!: {e}")


    
    async def send_menu(self, chat_id: int, text: str, keyboard: dict) -> None:

        try:

            url = f"{self.base_url}/sendMessage"
        
            payload = {

            "chat_id": chat_id,
            "text": text,
            'parse_mode': 'HTML',
            "reply_markup": keyboard

            }
        
            await self.client.make_request(method="POST", url=url, json=payload)
            self.logger.info(f"Action: Telegram inline menu sent! to {chat_id}")
        
        except Exception as e:   
            self.logger.error(f"Error: Unable to send Telegram Inline to {chat_id}!: {e}")
    
    async def edit_menu(self, chat_id: int, message_id: int, new_text: str, current_menu: str, keyboard: dict):

        try:

            url = f"{self.base_url}/editMessageText"

            payload = {

            "chat_id": chat_id,
            "message_id": message_id,
            "text": new_text,
            'parse_mode': 'HTML',
            "reply_markup": keyboard

            }
        
            await self.client.make_request(method="POST", url=url, json=payload)
            self.logger.info(f"Action: Telegram inline menu edit! to {chat_id}")
        
        except Exception as e:   
            self.logger.error(f"Error: Unable to edit Telegram Inline menu to {chat_id}!: {e}")
    
    async def answer_callback_query(self, callback_query_id: int):
        url = f"{self.base_url}/answerCallbackQuery"

        payload = {

            "callback_query_id": callback_query_id,
            "text": "Pagina cambiata!",
            'parse_mode': 'HTML',
            "show_alert": False

        }

        await self.client.make_request(method="POST", url=url, json=payload)
        
    
    async def get_updates(self, offset=None, timeout=100):

        url = f"{self.base_url}/getUpdates"
        params = {"timeout": timeout, "offset": offset}
        response = await self.client.make_request(method="POST", url=url, params=params, timeout=timeout)
        return response.request_content.json()
    
    async def close(self):
        await self.client.aclose()

# Class assigned to elaborating updates from Telegram API, especially user's command on chat
class CommandProcessor:

    def __init__(self, bot: Callable, db: Callable):
        self.db = db
        self.bot = bot
        self.last_update_id = None
        self.logger = bot.logger
        self.processed_update_ids = set()

    # Long polling to Telegram API
    async def process_updates(self):

         while True:

            try:

                self.logger.info(f"Requesting updates with offset: {self.last_update_id}")
                updates = await self.bot.get_updates(offset=self.last_update_id)

                if "result" in updates and len(updates["result"]) > 0:

                    for update in updates["result"]:
                        update_id = update['update_id']
                    
                        self.logger.info(f"Processing update_id: {update_id}")
                        await self.handle_update(update)
                        self.last_update_id = update_id + 1
                
                    self.logger.info(f"Updated last_update_id to: {self.last_update_id}")
                else:
                    self.logger.info("No new updates found.")
                
                await asyncio.sleep(1) 
            
            except Exception as e:
                self.logger.error({e})
        
    
    
    async def handle_update(self, update: dict):

        self.logger.info(f"Handling update_id: {update['update_id']}")

        if "callback_query" in update:

            callback_query = update["callback_query"]
            callback_data = callback_query["data"]
            chat_id = callback_query["message"]["chat"]["id"]
            message_id = callback_query["message"]["message_id"]
            callback_query_id = callback_query["id"]

            if callback_data == "menu_0":

                message = f"Personalize here"

                keyboard = {

                                "inline_keyboard": [

                                                    [{"text": "Commands 💡", "callback_data": "menu_1"}],
                                                    [{"text": "Settings ⚙️", "callback_data": "menu_settings"}],
                                                    [{"text": "Github 💻", "url": "https://github.com/Bomberfra23/Amazon-IT-Price-Tracker"}]
                                                        
                                                    ]                 

                            }

                await self.bot.edit_menu(chat_id, message_id, message, "menu_0", keyboard)
            
            elif callback_data == "menu_settings":

                email = await self.db.get_email_status(chat_id)

                if email:

                    message = f"🛠 <b>Settings Menu</b> 🛠\n\n✉️ Email Status: <b>Configured</b>✅\n<code>{email}</code>"

                    keyboard = {


                              "inline_keyboard" : [
                                  
                                                   [{"text" : "Remove Email 📭", "callback_data" : "delete_email"}],
                                                   [{"text" : "Back ↩️", "callback_data" : "menu_0"}]

                                                  ]


                                }
                
                else:

                    message = f"🛠 <b>Settings Menu</b> 🛠\n\n✉️ Email Status: <b>Not configured</b> ❌"

                    keyboard = {


                              "inline_keyboard" : [
                                  
                                                   [{"text" : "Add Email 📬", "callback_data" : "add_email"}],
                                                   [{"text" : "Back ↩️", "callback_data" : "menu_0"}]

                                                  ]


                                }
                
                await self.bot.edit_menu(chat_id, message_id, message, "menu_settings", keyboard)

            elif callback_data == "menu_1":

                message = "<code>/monitor</code>  In order to monitoring a product\n\n<code>/delete</code>  In order to stop monitoring a product\n\n<code>/summary</code> In order to visualize the monitor's list"

                keyboard = {

                                 "inline_keyboard": [

                                                    [{"text": "Back ↩️", "callback_data": "menu_0"}]
                                                        
                                                    ]                 

                            }
                
                await self.bot.edit_menu(chat_id, message_id, message, "menu_1", keyboard)
            
            elif callback_data == "delete_process":

                try:

                    del user_states[chat_id]
                    message = "Procedure cancelled ✅"
                    await self.bot.edit_message(chat_id, message_id, message)

                except:

                    message = "Impossible to cancel an already finished procedure ⚠️"
                    await self.bot.edit_message(chat_id, message_id, message)
            
            elif callback_data == "add_email":

                user_states[chat_id] = {"status" : "awaiting-add-email"}

                message = "✉️ Enter the email address you want to receive notifications on"

                keyboard = {

                                 "inline_keyboard": [

                                                    [{"text": "Cancel Procedure ↩️", "callback_data": "delete_process"}]
                                                        
                                                    ]                 

                            }
                
                await self.bot.edit_menu(chat_id, message_id, message, "add_email", keyboard)
            
            elif callback_data == "delete_email":

                await self.remove_email(chat_id, message_id)


            await self.bot.answer_callback_query(callback_query_id)

        if "message" in update:
            message = update.get("message", {})

            if "chat" in message and "text" in message:

                chat_id = message["chat"]["id"]
                text = message["text"]

                if chat_id in user_states:

                    if user_states[chat_id]["status"] == "awaiting-price":

                        try:
                            
                            price_target = float(text.strip().replace(",", "."))

                            if price_target > 0:

                                await self.monitor_asin(chat_id, user_states[chat_id]["asin"], price_target)
                                del user_states[chat_id]
                            
                            else:

                                await self.bot.send_message(chat_id, "Price target not valid. Try again ❌")
                        
                        except ValueError:

                            await self.bot.send_message(chat_id, "Price target not valid. Try again ❌")



                    if user_states[chat_id]["status"] == "awaiting-add-asin":

                        data = text.strip()

                        if len(data) == 10 and re.match(r'^[A-Z0-9]{10}$', data):

                            asin = data
                        
                        else:

                            asin = await self.extract_asin(text.strip())

                        if asin:

                            user_states[chat_id]["status"] = "awaiting-price"
                            user_states[chat_id]["asin"] = asin

                            message = "Now choose the price below which you want to be notified! 📉"
                                
                            keyboard = {

                                 "inline_keyboard": [

                                                    [{"text": "Cancel Procedure ↩️", "callback_data": "delete_process"}]
                                                        
                                                    ]                 

                            }

                            await self.bot.send_menu(chat_id, message, keyboard)

                        else:

                            await self.bot.send_message(chat_id, "Link or ASIN not valid. Try again ❌")
                    
                    if user_states[chat_id]["status"] == "awaiting-delete-asin":

                        data = text.strip()

                        if len(data) == 10 and re.match(r'^[A-Z0-9]{10}$', data):

                            asin = data
                        
                        else:

                            asin = await self.extract_asin(text.strip())

                        if asin:

                            await self.delete_asin(chat_id, asin)
                        
                        else:

                            await self.bot.send_message(chat_id, "Link or ASIN not valid. Try again ❌")
                    
                    if user_states[chat_id]["status"] == "awaiting-add-email":

                        email = text.strip()
                        await self.configure_email(chat_id, email)
                        




                if text == "/start":

                    message = f"Personalize here"

                    keyboard = {

                                "inline_keyboard": [

                                                    [{"text": "Commands 💡", "callback_data": "menu_1"}],
                                                    [{"text": "Settings ⚙️", "callback_data": "menu_settings"}],
                                                    [{"text": "Github 💻", "url": "https://github.com/Bomberfra23/Amazon-IT-Price-Tracker"}]
                                                        
                                                    ]                 

                            }

                    await self.bot.send_menu(chat_id, message, keyboard)
                
                if text.startswith("/monitor"):

                    message = "Enter the link or ASIN code of the product you want to track 🔗"

                    keyboard = {

                                 "inline_keyboard": [

                                                    [{"text": "Cancel Procedure ↩️", "callback_data": "delete_process"}]
                                                        
                                                    ]                 

                                }

                    await self.bot.send_menu(chat_id, message, keyboard)
                    user_states[chat_id] = {"status" : "awaiting-add-asin"}
                
                if text.startswith("/delete"):

                    message = "Enter the link or ASIN code of the product you want to track 🔗"

                    keyboard = {

                                 "inline_keyboard": [

                                                    [{"text": "Cancel Procedure ↩️", "callback_data": "delete_process"}]
                                                        
                                                    ]                 

                                }

                    await self.bot.send_menu(chat_id, message, keyboard)
                    user_states[chat_id] = {"status" : "awaiting-delete-asin"}
                
                if text.startswith("/summary"):

                   monitored_products = await self.db.get_monitored_products_by_user(chat_id)

                   if monitored_products:
                       
                       main_text = f"Your current monitoring list 📄\n\n"
                       product_text = ""

                       for product in monitored_products:
                           
                           product_text = product_text + f"<b>Title:</b> {product['title']}\n\n<b>ASIN:</b> <code>{product['asin']}</code>\n<b>Last price:</b> {product['last_price']}€\n<b>Price target:</b> {product['target_price']}€\n\n"
                        
                       await self.bot.send_message(chat_id, main_text + product_text)

                   else:
                       
                       await self.bot.send_message(chat_id, f"No products currently monitored, start doing so with <code>/monitor</code> ⚠️")


    
    async def monitor_asin(self, chat_id: int, asin: str, price_target: int) -> None:

        user_id = await self.db.user_exists(chat_id)

        if user_id is None:
            await self.db.add_user(chat_id)
            user_id =  await self.db.user_exists(chat_id)

        user_id = user_id[0]  
        asin_id = await self.db.asin_exists(asin)

        if asin_id is None:
            await self.db.add_asin(asin)
            asin_id = await self.db.asin_exists(asin)

        asin_id = asin_id[0]    
        link_exists = await self.db.link_exists(chat_id, asin)

        if link_exists is None:

            await self.db.link_user_to_asin(chat_id, asin, price_target)
            await self.bot.send_message(chat_id, f"ASIN {asin} added to tracking list with target price {price_target}€ ✅")
            del(user_states[chat_id])
        else:

            await self.bot.send_message(chat_id, f"ASIN {asin} is already monitored for this chat. ⚠️")
    
    async def delete_asin(self, chat_id: int, asin: str) -> None:

        link_exists = await self.db.link_exists(chat_id, asin)

        if link_exists is None:

            await self.bot.send_message(chat_id, f"Product {asin} is not present in your monitoring list ⚠️")
        
        else:

            await self.db.delete_link(chat_id, asin)
            await self.bot.send_message(chat_id, f"Product {asin} has been successfully removed from your watch list ✅")
            del(user_states[chat_id])
    
    async def configure_email(self, chat_id: int, email: str) -> None:
        
        is_valid = await self.is_valid_email(email)

        if is_valid:

            user = await self.db.user_exists(chat_id)

            if user is None:

                await self.db.add_user(chat_id)
                            
            await self.db.add_email(email, chat_id)

            message = "Email set up correctly, you will soon receive notifications in your inbox ✅"

            keyboard = {

                "inline_keyboard": [

                                    [{"text": "Back to menu ↩️", "callback_data": "menu_settings"}]
                                                        
                                    ]                 

                        }

            await self.bot.send_menu(chat_id, message, keyboard)
            del(user_states[chat_id])
            self.logger.info(f"Successfully added {email} to User {chat_id}")
                        
        else:

             await self.bot.send_message(chat_id, "Email not valid, try again ❌")
    
    async def remove_email(self, chat_id: int, message_id: int) -> None:

        await self.db.delete_email(chat_id)

        message = "✉️ email deleted ✅"

        keyboard = {

                            "inline_keyboard": [

                                            [{"text": "Back to menu ↩️", "callback_data": "menu_settings"}]
                                                        
                                            ]                 

                    }
                
        await self.bot.edit_menu(chat_id, message_id, message, "delete_email", keyboard)
        self.logger.info(f"Successfully deleted Email from  User {chat_id}")


    
    async def extract_asin(self, url: str) -> str:

        parsed_url = urlparse(url)

        if "amazon.it" in parsed_url.netloc:

            pattern = r'/([A-Z0-9]{10})(?:[/?]|$)'
            match = re.search(pattern, parsed_url.path)

            if match:
                return match.group(1)
        
        elif "amzn.eu" in parsed_url.netloc or "amzn.to" in parsed_url.netloc or "voob.it" in parsed_url.netloc:

            resolved_url = await self.resolve_redirect(url)

            if resolved_url:

                return await self.extract_asin(resolved_url)
            
            else:

                None
        
        else:

            return None
        
    async def is_valid_email(self, email: str) -> str:

        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None
    
    async def resolve_redirect(self, url: str) -> str:

        try:

            response = await self.bot.client.make_request("GET", url)
            return str(response.url)
        
        except Exception as e:

            self.logger.error(f"Unable to resolve the redirect -> {e}")
            return None




        


