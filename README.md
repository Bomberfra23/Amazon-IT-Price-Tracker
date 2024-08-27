<a href="https://docs.python.org/3.12/" target="_blank"><img src="https://badgen.net/badge/icon/Python 3.12 ?icon=pypi&label" ></a>
<a href="https://docs.python.org/3.12/" target="_blank"><img src="https://badgen.net/static/License/GPL 3.0/orange" ></a>
<a href="https://t.me/HwGroupTech" target="_blank"><img src="https://badgen.net/badge/icon/Telegram support?icon=telegram&label" ></a>

# ⚡️Amazon-IT-Price-Tracker ⚡️

Multiplatform automated Amazon IT Price Tracker with several type of alerts and configurations

## ⬆️ NEW UPDATE! V0.0.2 has been released!

- Bug Fix

- Up To 10% Improved Performance

- Added Vendors And Ratings For Every Product

- Added Alerts Testing Comand

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

### settings.py

This file is the main settings file.

1️⃣ Open settings.py file using text editor or IDE and fill in all fields. (for Telegram alert you need to create a BOT
using @botfather)

![Settings.py Image](https://github.com/Bomberfra23/Amazon-IT-Price-Tracker/blob/v0.0.1/images/settingsImage.png)

### ASIN.json

This file contains all the Amazon IT products informations

1️⃣ Find Amazon IT product unique ASIN code and copy it.

![Amazon IT ASIN Image](https://github.com/Bomberfra23/Amazon-IT-Price-Tracker/blob/v0.0.1/images/ASIN_Image.png)

2️⃣ Choose a price below which you want to be notified, choose the notification method and fill in the JSON file as
below.

![JSON file Image](https://github.com/Bomberfra23/Amazon-IT-Price-Tracker/blob/v0.0.1/images/json_image.png)

This is an example with 3 products but you can add up to 10.000 products!

## 🚀 Getting Started

Let's start the main script!

```shell
cd Amazon-IT-Price-Tracker
python3 main.py
```

![Main Menu Image](https://github.com/Bomberfra23/Amazon-IT-Price-Tracker/blob/v0.0.1/images/mainmenu_Image.png)

if you see this screen probably you are on the right way. Just configure two more options and we are ready!

### Threads Setting

In order to make several requests in parallel, this software has a multi-thread workflow. The more threads you enable,
the more products you can monitor at the same time but
also the more CPU, RAM and I/O you will consume. If you have very powerful hardware/internet bandiwdth and want to have
the greatest performance from this software, my advice is
to set the number of threads equal to the number of product that you have filled in. If you have like thousands of
products and speed is not a problem, my advice is to set the number
of threads equal to double the number of CPU cores that you have.
![Thread Setting Image](https://github.com/Bomberfra23/Amazon-IT-Price-Tracker/blob/v0.0.1/images/threadsetting_image.png)

### Delay Time Setting

You can also configure the delay time in seconds between cycle of product monitoring tasks. My advice is that the
perfect number is around 900 seconds.
![Delay Setting Image](https://github.com/Bomberfra23/Amazon-IT-Price-Tracker/blob/v0.0.1/images/delaysetting_image.png)

### Products Scraping

Once you have configured all the previous settings, Amazon IT Price Tracker will start to monitoring products for you.
Directly on the console you can see real-time information for every product:
request time, title and actual price.

![Product Image](https://github.com/Bomberfra23/Amazon-IT-Price-Tracker/blob/v0.0.1/images/product_Image.png)

## 📉 Alerts

When any monitored products' price drops under or equal to the selected target price, Amazon IT Price Tracker will warn
you via email or Telegram Bot message. (more features on the way).

### Telegram Alert

If Telegram message alert is enabled for that specific product, you will see this message on the console.

![Telegram Alert Image](https://github.com/Bomberfra23/Amazon-IT-Price-Tracker/blob/v0.0.1/images/telegramalert_Image.png)

And then you will receive your message directly in chat.

![Telegram Message Image](https://github.com/Bomberfra23/Amazon-IT-Price-Tracker/blob/v0.0.1/images/telegrammessage_Image.png)

### Email Alert

If Email alert is enabled for that specific product, you will see this message on the console.

![Email Alert Image](https://github.com/Bomberfra23/Amazon-IT-Price-Tracker/blob/v0.0.1/images/emailalert_Image.png)

And then you will receive your message directly in your email client.

![Email Message Image](https://github.com/Bomberfra23/Amazon-IT-Price-Tracker/blob/v0.0.1/images/email_Image.png)

## 👨‍💻 Support and Updates

This software will receive constant updates, follow my profile and star my repo. Actually we are in ALPHA Version so
maybe there are several bugs and problems
which I am not aware of. In order to report bugs and problems, please contact me on Telegram https://t.me/bomberfra23
or https://t.me/hwgrouptech





