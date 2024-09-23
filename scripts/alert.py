from email.mime.multipart import MIMEMultipart
from typing import Callable
from email.mime.text import MIMEText
from email.header import Header
import smtplib

from config.settings import (
    EMAIL_SMTP_SERVER,
    EMAIL_HOST_PASSWORD,
    EMAIL_HOST_USER,
    EMAIL_PORT,
    EMAIL_USE_TLS,
)


 # Class method assigned to send Email notification using .env configuration

class AlertManager:

    __slots__ = ("logger", "email_host", "email_smtp_port", "email_password", "email_use_tls", "email_smtp_server")

    def __init__(self, logger: Callable):

        self.logger = logger
        self.email_host = EMAIL_HOST_USER
        self.email_smtp_port = EMAIL_PORT
        self.email_password = EMAIL_HOST_PASSWORD
        self.email_use_tls = EMAIL_USE_TLS
        self.email_smtp_server = EMAIL_SMTP_SERVER
    
    def verify_server_configuration(self) -> bool:

        try:
            self.logger.info("Connecting to SMTP Server ...")

            server = smtplib.SMTP(self.email_smtp_server, self.email_smtp_port, timeout=10)

            self.logger.info("Successfully connected to SMTP Server ✓")

            if self.email_use_tls:
                self.logger.info("Using TLS encryption...")
                server.starttls()
                self.logger.info("TLS encryption enabled ✓")
            
            self.logger.info(f"Try to login with {self.email_host} and password ...")

            server.login(self.email_host, self.email_password)

            self.logger.info(f"Logged in with credentials ✓")
            server.quit()
            return True
        
        except smtplib.SMTPAuthenticationError:
            self.logger.error(f"SMTP Server authentication error {self.email_smtp_server}:{self.email_smtp_port} ✗")
            return False
        except smtplib.SMTPConnectError:
            self.logger.error(f"SMTP Server Connection error {self.email_smtp_server}:{self.email_smtp_port} ✗")
            return False
        except Exception as e:
            self.logger.error(f"SMTP Server Generic error -> {e} ✗")
            return False
        

    def send_email_message(self: classmethod, email_addressee: str, message: str) -> None:

        html_text = f"""   
  
        <html>
           <body>
             <p>{message}</p>
           </body>
        </html>

        """

        try:
            msg = MIMEMultipart()
            msg['From'] = Header(self.email_host, 'utf-8')
            msg['To'] = Header(email_addressee, 'utf-8')
            msg['Subject'] = Header("Amazon IT Price Tracker Alert", 'utf-8')
            msg.attach(MIMEText(html_text.encode('utf-8'), 'html', 'utf-8'))
            server = smtplib.SMTP(self.email_smtp_server, self.email_smtp_port)

            if self.email_use_tls:
                server.starttls()
            server.login(self.email_host, self.email_password)
            server.sendmail(self.email_host, email_addressee, msg.as_string())
            server.quit()

            self.logger.info(f"Action: Email Alert sent!")
            return

        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(f"SMTP Server Authentication Email Alert Error: {e}")

        except smtplib.SMTPConnectError as e:
            self.logger.error(f"SMTP Server Connection Email Alert Error: {e}")

        except smtplib.SMTPRecipientsRefused as e:
            self.logger.error(f"Address Refused Email Alert Error: {e}")

        except smtplib.SMTPDataError as e:
            self.logger.error(f"Data Email Alert Error: {e}")

        except smtplib.SMTPServerDisconnected as e:
            self.logger.error(f"SMTP Server Disconnected Email Alert Error: {e}")

        except smtplib.SMTPException as e:
            self.logger.error(f"Generic SMTP Server Email Alert Error: {e}")

        except Exception as e:
            self.logger.error(f"Generic Email Alert Error: {e}")
    