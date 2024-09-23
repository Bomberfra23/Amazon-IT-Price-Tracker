import logging, sys, os

from config.settings import SAVE_LOGS_TO_FILE

class Logger:

    __slots__ = ('logger', 'name')

    _instance = None

    # Singleton implementation of this class assigned to log every action in the program's flow

    def __new__(cls, name="AmazonITPriceTracker", file_save = SAVE_LOGS_TO_FILE):

        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.logger = logging.getLogger(name)
            cls._instance.logger.setLevel(logging.INFO) 

            if not cls._instance.logger.hasHandlers():
                console_handler = logging.StreamHandler()
                console_formatter = logging.Formatter("[%(levelname) 4s/%(asctime)s] %(name)s: %(message)s")
                console_handler.setFormatter(console_formatter)
                console_handler.stream = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
                cls._instance.logger.addHandler(console_handler)

                if file_save:
                    file_handler = logging.FileHandler(f"{os.getcwd()}/logs.log", encoding='utf-8')
                    file_formatter = logging.Formatter("[%(levelname) 4s/%(asctime)s] %(name)s: %(message)s")
                    file_handler.setFormatter(file_formatter)
                    cls._instance.logger.addHandler(file_handler)
        
        return cls._instance
    
    # return the instance of the class

    def get_logger(self) -> callable:
        return self._instance.logger

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def critical(self, message: str) -> None:
        self.logger.critical(message)
    