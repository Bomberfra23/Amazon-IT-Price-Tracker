from typing import Tuple
from lxml import html
from config import settings
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, EMAIL_SMTP_SERVER, EMAIL_HOST_PASSWORD, EMAIL_HOST_USER, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_ADDRESSEE
import datetime, sys, re
import json, urllib3
from random_user_agent.params import SoftwareName, OperatingSystem, SoftwareEngine, HardwareType, SoftwareType
from random_user_agent.user_agent import UserAgent
import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib3.exceptions import HTTPError, MaxRetryError, TimeoutError


# Client User-Agent random generator variables
software_names = [SoftwareName.CHROME.value, SoftwareName.EDGE.value, SoftwareName.FIREFOX.value, SoftwareName.ANDROID.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
software_engines = [SoftwareEngine.GECKO.value, SoftwareEngine.WEBKIT.value, SoftwareEngine.BLINK.value]
hardware_types = [HardwareType.MOBILE.value, HardwareType.COMPUTER.value, HardwareType.SERVER.value]
software_types = [SoftwareType.WEB_BROWSER.value]
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, hardware_types=hardware_types, software_engines=software_engines, software_types=software_types, limit=100)

# those lists and dicts contains the JSON's dataset in order to be processed by the thread's pool in main.py
urls = list() 
price_targets = list()
telegram_alerts_settings = list()
email_alerts_settings = list()
last_prices = dict()

http_client = urllib3.PoolManager() # https requests pool manager

# functions assigned to manage the start input values on the main screen

# main scraper Class
class AmazonScraper:
     
    def __init__ (self, url: str):
          self.url = url
    
    # Class method assigned to making http requests using http pool manager
    def make_request(self: classmethod, method = "GET", headers = None, params = None, data=None, timeout = 5.0, retries = 2, parse_json=False) -> dict:  

        if headers is None:
            headers = {}

        try:

            encoded_data = None
            if data:
                if isinstance(data, dict):
                    encoded_data = json.dumps(data).encode('utf-8')
                    headers['Content-Type'] = 'application/json'

                else:
                    encoded_data = data
            
            response = http_client.request(

                method = method,
                url = self.url, 
                fields = params, 
                body = encoded_data, 
                headers = headers,
                timeout = timeout,
                preload_content = False
                
            )

            data = response.data

            if parse_json:
                data = json.loads(data.decode('utf-8'))
                return {

                'status_code' : response.status,
                'data' : data,
                'error' : None
                }
            
            else:
                tree = html.fromstring(data)
                return {

                'status_code' : response.status,
                'data' : tree,
                'error' : None

                }
            
        except MaxRetryError as e:
            
            return {

            'status_code': None,
            'data': None,
            'error': f"Max retries exceeded -> {str(e)}"

            }
        
        except TimeoutError as e:

            return {

            'status_code': None,
            'data': None,
            'error': f"Request timed out -> {str(e)}"

            }
        
        except HTTPError as e:
            
            return {

            'status_code': None,
            'data': None,
            'error': f"HTTP error occurred -> {str(e)}"

            }
        except json.JSONDecodeError as e:

            return {

            'status_code': None,
            'data': None,
            'error': f"JSON decode error -> {str(e)}"

            }
        except Exception as e:

            return {

            'status_code': None,
            'data': None,
            'error': f"An unexpected error occurred -> {str(e)}"

            }
        finally:

            if 'response' in locals():
                response.release_conn()

    # Class method assigned to scraping the html_content output of the previous function
    def scrape_amazon_product(self: classmethod, response: dict) -> Tuple[float|str, str]:  

        timestamp: str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if not response['error']:

            try:

                html_tree = response['data']
                title = html_tree.cssselect('#productTitle')[0].text_content().strip() # finds title
                price_path = html_tree.cssselect('#apex_offerDisplay_desktop')

                if price_path != []:

                    m = re.search(r'\d{1,3}?\.?\d{1,3}\,\d{1,2}', price_path[0].text_content().strip(), re.IGNORECASE) # finds price
                    price = float(m.group(0).replace(".","").replace(",", ".").replace("€", "")) # converts and formats the finded price

                else:

                    price = "Out of Stock / No Offer" 
                
                vendor_list = html_tree.cssselect('#merchantInfoFeature_feature_div > div.offer-display-feature-text > div > span')

                if vendor_list != []:
                    
                    vendor = vendor_list[0].text_content().strip()
                
                else:

                    vendor = "N/A"
                
                rating_list = html_tree.cssselect('#acrPopover > span.a-declarative > a > span')

                if rating_list != []:

                    rating = float(rating_list[0].text_content().strip().replace(",", "."))
                    
                else:

                    rating = 0
        
                print(f"[{timestamp}]  Object: {title}  Price: {price}€  Vendor: {vendor}  Rating: {rating}")
                return price, title, vendor, rating
            
            except Exception as error: # errors handling
                print(f"[{timestamp}]  Generic Scraping Data Error: {error}")

        else:

            print(f"[{timestamp}] HTTP Error: {response['error']}")
            return None, None, None, None
    
    # Class method assigned to send Telegram notification using settings.py configuration
    def telegram_message(self: classmethod, telegram_bot_token: str, telegram_chat_id: str, text: str) -> None: 
        timestamp: str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        API_call: str = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"

        data = {

            'chat_id' : telegram_chat_id,
            'text' : text,
            'parse_mode' : 'HTML'

        }

        result = AmazonScraper(API_call).make_request(method='POST', data=data, parse_json=True) # makes request to Telegram API Server

        if result['error'] or not result['data']['ok'] or result['status_code'] != 200:

            print(f"[{timestamp}]  Error: Unable to send Telegram Alert!")

        else:

            print(f"[{timestamp}]  Action: Telegram Alert sended!")
    
    # Class method assigned to send Email notification using settings.py configuration
    def email_message(self: classmethod, smtp_server: str, smtp_port: int, use_tls: bool, from_email: str, password: str, to_email: str, text: str) -> None: 

        html_text = f"""   
  
        <html>
           <body>
             <p>{text}</p>
           </body>
        </html>

        """

        try:

            timestamp: str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = "Amazon IT Price Tracker Alert"
            msg.attach(MIMEText(html_text, 'html'))
            server = smtplib.SMTP(smtp_server, smtp_port)

            if use_tls:
                server.starttls()
            server.login(from_email, password)
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            server.quit()

            print(f"[{timestamp}]  Action: Email Alert sended!")

        except smtplib.SMTPAuthenticationError as e:
            print(f"[{timestamp}]  SMTP Server Authentication Email Alert Error: {e}")

        except smtplib.SMTPConnectError as e:
            print(f"[{timestamp}]  SMTP Server Connection Email Alert Error: {e}")

        except smtplib.SMTPRecipientsRefused as e:
            print(f"[{timestamp}]  Addresee Refused Email Alert Error: {e}")

        except smtplib.SMTPDataError as e:
            print(f"[{timestamp}]  Data Email Alert Error: {e}")

        except smtplib.SMTPServerDisconnected as e:
            print(f"[{timestamp}]  SMTP Server Disconnected Email Alert Error: {e}")

        except smtplib.SMTPException as e:
            print(f"[{timestamp}]  Generic SMTP Server Email Alert Error: {e}")

        except Exception as error:
            print(f"[{timestamp}]  Generic Email Alert Error: {e}")
    
# function assigned to reading JSON file and extracting Amazon products, prices and alert configurations. Lists and dicts are initalized with those datas.
def read_data() -> None:

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}]  Action: Starting...")

    try:

        with open('config/ASIN.json') as file_input:
            data = json.load(file_input)
            file_input.close()

        for product in data['amazon_it_products']:
            ASIN = str(product['ASIN'])
            price_target = float(product['price_target'])
            telegram_alert_setting = bool(product['telegram_alert'])
            email_alert_setting = bool(product["email_alert"])
            url = f'https://amazon.it/dp/{ASIN}'
            last_prices[url] = 0.0
            urls.append(url)
            price_targets.append(price_target)
            telegram_alerts_settings.append(telegram_alert_setting)
            email_alerts_settings.append(email_alert_setting)

        print(f"[{timestamp}]  Action: Successfully loaded {len(urls)} Amazon IT Products!")

    except Exception as error:
        print(f"[{timestamp}]  Generic Error: {error}")
        sys.exit()

# function assigned to combine all the previous functions
def task(url: str, price_target: float|str, telegram_alert_setting: bool, email_alert_setting: bool) -> None:
     
     headers: dict = {'User-Agent' : user_agent_rotator.get_random_user_agent(), "Accept" : "text/html"}
     response = AmazonScraper(url).make_request(headers=headers)
     price, title, vendor, rating = AmazonScraper(url).scrape_amazon_product(response)

     if type(price) == float and price<=price_target and (price<last_prices[url] or last_prices[url] == 0.0):
          
          text = f"<b>{title}</b>\n\nRating: {rating} {int(round(rating))*'⭐️'}\nVendor: {vendor}\nStatus: Available ✅\nPrice: <b>{price}€</b> <del>{last_prices[url]}€</del>\n\n🔗Link: {url}"

          if telegram_alert_setting:
              
              AmazonScraper(url).telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, text)

          if email_alert_setting:
              
              AmazonScraper(url).email_message(EMAIL_SMTP_SERVER, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_ADDRESSEE, text)

     last_prices[url] = price

# functions assigned to get user's input in the main page

def get_threads_input() -> int:

    value = input("Insert the number of threads:   ")

    if value.isnumeric() and int(value) > 0:
        return int(value)
    
    else:
        print("Invalid Input! try again.")
        return get_threads_input()

def get_delay_input() -> int:

    value = input("Insert the number of seconds of delay:  ")

    if value.isnumeric() and int(value) >= 0:
        return int(value)
    
    else:
        print("Invalid Input! try again.")
        return get_delay_input()

# functions assigned to check if alerts work properly 

def check_telegram_alert() -> None:
    timestamp: str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    value = input("Do You Want To Check If Telegram Alert Works Properly? [Y/n]  ")

    if value.isalpha() and value == 'Y':
        print(f"[{timestamp}]  Action: Checking Telegram API...")
        text = "Telegram Alert Service has been started ✅"
        AmazonScraper(None).telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, text)
    
    elif value.isalpha() and value == 'n':
        print(f"[{timestamp}]  Action: Telegram API Check has been skipped")
    
    else:
        print("Invalid Input! try again.")
        return check_telegram_alert()

def check_email_alert() -> None:
    timestamp: str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    value = input("Do You Want To Check If Email Alert Works Properly? [Y/n]  ")

    if value.isalpha() and value == 'Y':
        print(f"[{timestamp}]  Action: Checking Email Alert Service...")
        text = "Email Alert Service has been started ✅"
        AmazonScraper(None).email_message(EMAIL_SMTP_SERVER, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_ADDRESSEE, text)
    
    elif value.isalpha() and value == 'n':
        print(f"[{timestamp}]  Action: Email Alert Service Check has been skipped")
    
    else:
        print("Invalid Input! try again.")
        return check_email_alert()








            


