<a href="https://docs.python.org/3.12/" target="_blank"><img src="https://badgen.net/badge/icon/Python 3.12 ?icon=pypi&label" ></a>
<a href="https://docs.python.org/3.12/" target="_blank"><img src="https://badgen.net/static/License/GPL 3.0/orange" ></a>
<a href="https://t.me/HwGroupTech" target="_blank"><img src="https://badgen.net/badge/icon/Telegram support?icon=telegram&label" ></a>

# ⚡️Amazon-IT-Price-Tracker ⚡️

Multiplatform automated Amazon IT Price Tracker with several type of alerts and configurations

## ⬆️ NEW UPDATE! V0.1.0 BETA has been released!

- Huge Bug Fix

- Up To 2x Improved Performance Thanks to Multiprocessing and Asynchronous Implementation

- New Ecosystem Based on Multi-User Telegram BOTs
  
- New SQLite Ultra Fast Database Instead of JSON

---

## 📄 Disclaimer

> This Amazon IT Price Tracker is provided for educational and research purposes only. By using this Software, you agree
> to comply with local and international laws regarding data scraping and privacy. The authors and contributors are not
> responsible for any misuse of this software. This tool should not be used to violate the rights of others, for unethical
> purposes, or to use data in an unauthorized or illegal manner.

For any concerns, please contact me on Telegram by clicking its icon. I will promptly reply.

## 📦 Requirements

To install and use this script you need:

- Python 3.x installed (recommended Python 3.12.4 or newer)
- At least 30Mbps Download/Upload Internet Connection (recommended 100Mbps or higher), 1GB of RAM, Dual-Core CPU

## 📥 Install

Download files on your PC using git clone or download ZIP

```shell
git clone https://github.com/Bomberfra23/Amazon-IT-Price-Tracker
cd Amazon-IT-Price-Tracker
```

### Windows

Open Windows PowerShell or CMD and start the automatic installer program, it will take care of everything for you.

```shell
cd Amazon-IT-Price-Tracker
.\setup.bat
```

![Windows Install GIF](https://github.com/Bomberfra23/Amazon-IT-Price-Tracker/blob/v0.0.1/images/WindowsInstall.gif)

### MacOS / Linux

Open Terminal and start the automatic installer program, it will take care of everything for you.
```shell
cd Amazon-IT-Price-Tracker
chmod +x setup.sh
./setup.sh
```

## ⚙️ Configuration

### .env File

This file is the main settings file.

1️⃣ Open .env file using text editor or IDE and fill in all fields. (You need to create a BOT
using @botfather and to use your univoque Telegram Chat ID)

![.env Configuration Image](https://github.com/Bomberfra23/Amazon-IT-Price-Tracker/blob/v0.0.2/images/env-configuration.png)


## 🚀 Getting Started

Let's start the main script!

```shell
cd Amazon-IT-Price-Tracker
python3 main.py
```

![Main Menu Image](https://github.com/Bomberfra23/Amazon-IT-Price-Tracker/blob/v0.0.1/images/mainmenu_Image.png)

If you see this screen probably you are on the right way. Now, pressing any key, the script will test all the credentials 
and configuration in the .env that you have filled in. It will be enough for just one not to be valid to prevent the program 
from starting, so check carefully.

![Check Config Image]()

### 🤖 Telegram BOT

Once the script has started, the messaging service via Telegram Bot will start. Reach your @ of your Telegram BOT and enter <code>/start</code>

![Start Telegram BOT Image]()

This is a Telegram BOT capable of offering centralized control of product scraping! It can be used by hundreds of users simultaneously to monitor
what they like best and be notified of personalized offers! Let's the integrated commands.

![Telegram BOT Commands GIF]()

#### Monitor Command

<code>/monitor</code> is used for entering a new product to your personal list and, in case it's not already present, also in the Database. Is very simple,
you need only to enter the Amazon IT product's link or ASIN.

![Monitor Command GIF]()

#### Delete Command

<code>/delete</code> is used for deleting a product from your personal list. Also in this case you only need to enter the Amazon IT product's link or ASIN.

![Delete Command GIF]()

#### Summary Command

<code>/summary</code> is used for visualyzing your personal actual monitor list. You be able to see all your monitored products with some information like 
title, ASIN, last price, price target.

#### Email Settings


## 📉 Alerts

When any monitored products' price drops under or equal to the selected target price, Amazon IT Price Tracker will warn
you via email or Telegram Bot message. (more features on the way).

### Telegram Alert

If Telegram message alert is enabled for that specific product, you will see this message on the console.

![Telegram Alert Image](https://github.com/Bomberfra23/Amazon-IT-Price-Tracker/blob/v0.0.2/images/telegramalert_Image.png)

And then you will receive your message directly in chat.

![Telegram Message Image](https://github.com/Bomberfra23/Amazon-IT-Price-Tracker/blob/v0.0.2/images/telegram-message.png)

### Email Alert

If Email alert is enabled for that specific product, you will see this message on the console.

![Email Alert Image](https://github.com/Bomberfra23/Amazon-IT-Price-Tracker/blob/v0.0.1/images/emailalert_Image.png)

And then you will receive your message directly in your email client.

![Email Message Image](https://github.com/Bomberfra23/Amazon-IT-Price-Tracker/blob/v0.0.2/images/email-alert.png)

## 👨‍💻 Support and Updates

This software will receive constant updates, follow my profile and star my repo. Actually we are in ALPHA Version so
maybe there are several bugs and problems
which I am not aware of. In order to report bugs and problems, please contact me on Telegram https://t.me/bomberfra23
or https://t.me/hwgrouptech





