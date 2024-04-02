
import sqlite3

def connect_to_db():
    return sqlite3.connect('telegram_bot.db') 


conn = connect_to_db()
cursor = conn.cursor()

# # Contoh membuat tabel
cursor.execute('''
        CREATE TABLE IF NOT EXISTS inbox (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            message_date TEXT NOT NULL,
            message_text TEXT NOT NULL,
            pesan TEXT NOT NULL  
        )
    ''')

cursor.execute('''
        CREATE TABLE IF NOT EXISTS outbox (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            message_text TEXT NOT NULL,
            sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')


conn.commit()
conn.close()
