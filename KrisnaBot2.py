import os
import telebot
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

# Function to connect to the SQLite database
def connect_to_db():
    return sqlite3.connect('telegram_bot.db')  # SQLite database file name

# Create tables if they don't exist
def create_tables():
    conn = connect_to_db()
    cursor = conn.cursor()
    # Create inbox table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inbox (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            message_date TIMESTAMP NOT NULL,
            message_text TEXT NOT NULL
        )
    ''')
    # Create outbox table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS outbox (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            message_text TEXT NOT NULL,
            sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Create preset_messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preset_messages (
            id INTEGER PRIMARY KEY,
            input_message TEXT NOT NULL,
            output_message TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to insert incoming message to inbox table
def insert_inbox_message(user_id, username, message_date, message_text):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO inbox (user_id, username, message_date, message_text) VALUES (?, ?, ?, ?)",
                   (user_id, username, message_date, message_text))
    conn.commit()
    conn.close()

# Function to insert outgoing message to outbox table
def insert_outbox_message(user_id, message_text):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO outbox (user_id, message_text) VALUES (?, ?)", (user_id, message_text))
    conn.commit()
    conn.close()

# Function to retrieve preset response from preset_messages table
def get_preset_response(input_message):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT output_message FROM preset_messages WHERE input_message = ?", (input_message,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

# Handler for messages other than commands
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    username = message.from_user.username
    message_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message_text = message.text

    # Check if message is empty
    if not message_text:
        response = "Maaf, tidak ada pesan yang ditulis. Silakan tulis pesan yang ingin Anda sampaikan."
    else:
        # Check if the message matches any preset messages
        preset_response = get_preset_response(message_text)
        if preset_response:
            response = preset_response
        else:
            response = "Pesan Anda telah diterima dan akan segera diproses."

    bot.reply_to(message, response)
    insert_inbox_message(user_id, username, message_date, message_text)
    insert_outbox_message(user_id, response)

# Polling the bot
bot.polling()
