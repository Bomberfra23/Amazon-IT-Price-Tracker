import aiosqlite
from typing import Callable


# Class assigned to manage the creation and queries of the database

class DatabaseManager:
     
     __slots__ = ('logger', 'db_name', 'initialized')
    
     _instance = None  

     def __new__(cls, *args, **kwargs):

        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)

        return cls._instance

     def __init__(self, logger: Callable, db_name="db/amazon_bot.db"):

        if not hasattr(self, 'initialized'):  
            self.db_name = db_name
            self.logger = logger
            self.initialized = True  
    

     async def create_tables(self) -> None:
        
        async with aiosqlite.connect(self.db_name) as db:

            await db.execute('''
                CREATE TABLE IF NOT EXISTS User (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER UNIQUE,
                    email TEXT NULL
                )
            ''')

            await db.execute('''
                CREATE TABLE IF NOT EXISTS ASIN (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asin TEXT UNIQUE,
                    title TEXT,
                    last_price REAL
                )
            ''')

            await db.execute('''
                CREATE TABLE IF NOT EXISTS UserToAsin (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    asin_id INTEGER,
                    target_price REAL,
                    FOREIGN KEY (user_id) REFERENCES User(id),
                    FOREIGN KEY (asin_id) REFERENCES ASIN(id)
                )
            ''')

            await db.commit()
            self.logger.info("Database: Successfully Created Tables")
    
     async def add_user(self, chat_id: int) -> None:

        async with aiosqlite.connect(self.db_name) as db:

            await db.execute('''
                INSERT OR IGNORE INTO User (chat_id) 
                VALUES (?)
            ''', (chat_id,))

            await db.commit()
            self.logger.info(f"Database: Successfully Added User {chat_id}")
    
     async def add_asin(self, asin: str, title = "N/A", current_price=0.0) -> None:

        async with aiosqlite.connect(self.db_name) as db:

            await db.execute('''
                INSERT OR IGNORE INTO ASIN (asin, title, last_price) 
                VALUES (?, ?, ?)
            ''', (asin, title, current_price))

            await db.commit()
            self.logger.info(f"Database: Successfully Added ASIN {asin}")
    
     async def add_email(self, email: str, chat_id: int) -> None:
         
         async with aiosqlite.connect(self.db_name) as db:
             
             await db.execute('''
                  UPDATE User
                  SET email = ?
                  WHERE chat_id = ?
            ''', (email, chat_id))

             await db.commit()
    
     async def delete_email(self, chat_id: int) -> None:
         
         async with aiosqlite.connect(self.db_name) as db:
             
             await db.execute('''
                  UPDATE User
                  SET email = NULL
                  WHERE chat_id = ?
            ''', (chat_id,))

             await db.commit()
         
    
     async def update_last_price(self, asin: str, new_last_price: int) -> None:
         
        async with aiosqlite.connect(self.db_name) as db:

            await db.execute('''
                  UPDATE ASIN
                  SET last_price = ?
                  WHERE asin = ?
            ''', (new_last_price, asin))

            await db.commit()
    
     async def update_title(self, asin: str, new_title: str) -> None:
         
         async with aiosqlite.connect(self.db_name) as db:
             
            await db.execute('''
                  UPDATE ASIN
                  SET title = ?
                  WHERE asin = ?
            ''', (new_title, asin))

            await db.commit()
    
     async def get_all_asins(self) -> list:
        
        async with aiosqlite.connect(self.db_name) as db:

            async with db.execute('SELECT asin FROM ASIN') as cursor:

                rows = await cursor.fetchall()
                asins = [row[0] for row in rows]
                return asins
        
     async def get_all_users(self) -> list:
         
         async with aiosqlite.connect(self.db_name) as db:
             
            async with db.execute('SELECT chat_id FROM User') as cursor:

                rows = await cursor.fetchall()
                users = [row[0] for row in rows]
                return users
    
     async def get_email_status(self, chat_id: int) -> str:
         
         async with aiosqlite.connect(self.db_name) as db:
             
             async with db.execute('SELECT email FROM User WHERE chat_id = ?', (chat_id,)) as cursor:
                 
                email = await cursor.fetchone()
                if email is None:
                    return None
                return email[0]
    
     async def link_user_to_asin(self, chat_id: int, asin: str, target_price: int) -> None:

        async with aiosqlite.connect(self.db_name) as db:

            async with db.execute('SELECT id FROM User WHERE chat_id = ?', (chat_id,)) as cursor:
                user_id = await cursor.fetchone()
                if user_id is None:
                    raise ValueError("User not found")
                user_id = user_id[0]

            async with db.execute('SELECT id FROM ASIN WHERE asin = ?', (asin,)) as cursor:
                asin_id = await cursor.fetchone()
                if asin_id is None:
                    raise ValueError("ASIN not found")
                asin_id = asin_id[0]

            await db.execute('''
                INSERT INTO UserToAsin (user_id, asin_id, target_price) 
                VALUES (?, ?, ?)
            ''', (user_id, asin_id, target_price))

            await db.commit()
            self.logger.info(f"Database: Successfully Added ASIN {asin} to User's {chat_id} monitor list with price target {target_price}€")
    
     async def notify_users(self, asin: str, current_price: int) -> list:

        async with aiosqlite.connect(self.db_name) as db:

            async with db.execute('SELECT id, last_price FROM ASIN WHERE asin = ?', (asin,)) as cursor:
                asin_data = await cursor.fetchone()
                if asin_data is None:
                    raise ValueError("ASIN non trovato")
                asin_id, last_price = asin_data
            
            if current_price == last_price:
                return []

            async with db.execute('''
                SELECT u.chat_id
                FROM UserToAsin uta
                JOIN User u ON uta.user_id = u.id
                WHERE uta.asin_id = ? 
                AND (uta.target_price >= ?)
            ''', (asin_id, current_price)) as cursor:
                user_list = await cursor.fetchall()
                
            return user_list
    
     async def get_monitored_products_by_user(self, chat_id: int) -> dict:
   
        async with aiosqlite.connect(self.db_name) as db:
      
             async with db.execute('SELECT id FROM User WHERE chat_id = ?', (chat_id,)) as cursor:
                user_id = await cursor.fetchone()
                if user_id is None:
                    return []
                user_id = user_id[0]


             async with db.execute('''
                SELECT a.asin, a.title, a.last_price, uta.target_price
                FROM UserToAsin uta
                JOIN ASIN a ON uta.asin_id = a.id
                WHERE uta.user_id = ?
                ''', (user_id,)) as cursor:
                rows = await cursor.fetchall()

        monitored_products = []
        for row in rows:
            monitored_products.append({
                "asin" : row[0],
                "title" : row[1],
                "last_price" : row[2],
                "target_price" : row[3]
            })

        return monitored_products
    
     async def delete_link(self, chat_id: int, asin: str) -> None:

        async with aiosqlite.connect(self.db_name) as db:
 
            async with db.execute('SELECT id FROM User WHERE chat_id = ?', (chat_id,)) as cursor:
                user_id = await cursor.fetchone()
                if user_id is None:
                    raise ValueError("Utente non trovato")
                user_id = user_id[0]

       
            async with db.execute('SELECT id FROM ASIN WHERE asin = ?', (asin,)) as cursor:
                asin_id = await cursor.fetchone()
                if asin_id is None:
                    raise ValueError("ASIN non trovato")
                asin_id = asin_id[0]

           
            await db.execute('''
                DELETE FROM UserToAsin 
                WHERE user_id = ? AND asin_id = ?
            ''', (user_id, asin_id))

            await db.commit()
            self.logger.info(f"Database: Successfully Removed ASIN {asin} to User's {chat_id} monitor list")
        
     async def user_exists(self, chat_id: int) -> bool:
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT id FROM User WHERE chat_id = ?', (chat_id,)) as cursor:
                return await cursor.fetchone()

     async def asin_exists(self, asin: str) -> bool:
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT id FROM ASIN WHERE asin = ?', (asin,)) as cursor:
                return await cursor.fetchone()

     async def link_exists(self, chat_id: int, asin: str) -> bool:
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('''
                SELECT UserToAsin.id 
                FROM UserToAsin
                JOIN User ON User.id = UserToAsin.user_id
                JOIN ASIN ON ASIN.id = UserToAsin.asin_id
                WHERE User.chat_id = ? AND ASIN.asin = ?
            ''', (chat_id, asin)) as cursor:
                return await cursor.fetchone()