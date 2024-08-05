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

class AmazonScraper:      # main scraper Class
     
    def __init__ (self, url: str):
          self.url = url
    
    # function assigned to making http requests using random User-Agent and http pool manager
    def make_request(self: classmethod) -> bytes:    
        timestamp: str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        headers: dict = {'User-Agent': user_agent_rotator.get_random_user_agent()}
        try:
           response = http_client.request("GET", self.url, headers=headers)
           if response.status == 200:
              html_content: bytes = response.data
              return html_content   # returns html content in bytes when server status is 200                   
           elif response.status == 404:
              print(f'[{timestamp}]  Error: Page not found')
           else:
              print(f'[{timestamp}]  Error: Unexpected error')
        except urllib3.exceptions as error: # errors handling
              print(f'[{timestamp}]  HTTP Client Error: {error}')
        except Exception as error:
              print(f'[{timestamp}]  Generic Error: {error}')
        finally:
            response.release_conn()

    # function assigned to scraping the html_content output of the previous function
    def scrape_data(self: classmethod, response: str) -> Tuple[float|str, str]:  
        timestamp: str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            html_tree = html.fromstring(response)
            title = html_tree.cssselect('#productTitle')[0].text_content().strip() # finds title
            price_path = html_tree.cssselect('#apex_offerDisplay_desktop')
            if price_path != []:
                m = re.search(r'\d{1,3}?\.?\d{1,3}\,\d{1,2}', price_path[0].text_content().strip(), re.IGNORECASE) # finds price
                price = float(m.group(0).replace(".","").replace(",", ".").replace("€", "")) # converts and formats the finded price
            else:
                price = "Out of Stock / No Offer" 
        except Exception as error: # errors handling
            print(f"[{timestamp}]  Generic Scraping Data Error: {error}")
        print(f"[{timestamp}]  Object: {title}  Price: {price}€")
        return title, price
    
    # function assigned to send Telegram notification using settings.py configuration
    def telegram_alert(self: classmethod, telegram_bot_token: str, telegram_chat_id: str, title: str, price: float|str, url: str) -> None: 
        timestamp: str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        point_to_API: str = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage?chat_id={telegram_chat_id}&text={title}\n\nStatus: Available ✅\nPrice: {price}€\n\nLink: {url}"
        try:
            AmazonScraper(point_to_API).make_request() # makes request to Telegram API Server
            print(f"[{timestamp}]  Action: Telegram Alert sended!")
        except Exception as error: #errors handling 
            print(f"[{timestamp}]  Generic Telegram Alert Error: {error}")
    
    # function assigned to send Email notification using settings.py configuration
    def email_alert(self: classmethod, smtp_server: str, smtp_port: int, use_tls: bool, from_email: str, password: str, to_email: str, title: str, price: float|str, url: str) -> None: 
        timestamp: str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = "Amazon IT Price Tracker Alert"
        body = f"{title}\n\nStatus: Available ✅\nPrice: {price}€\n\nLink: {url}"
        msg.attach(MIMEText(body, 'plain'))
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            if use_tls:
                server.starttls()
            server.login(from_email, password)
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            server.quit()
            print(f"[{timestamp}]  Action: Email Alert sended!")
        except Exception as error:
            print(f"[{timestamp}]  Generic Email Alert Error: {error}")
    
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
            last_prices[url] = 1000000
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
     response = AmazonScraper(url).make_request()
     title, price = AmazonScraper(url).scrape_data(response)
     if type(price) == float and price<=price_target and price<last_prices[url]:
          if telegram_alert_setting:
              AmazonScraper(url).telegram_alert(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, title, price, url)
          if email_alert_setting:
              AmazonScraper(url).email_alert(EMAIL_SMTP_SERVER, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_ADDRESSEE, title, price, url)
     last_prices[url] = price




            


