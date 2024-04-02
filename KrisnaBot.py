import os
import telebot
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)


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

# Function to connect to the SQLite database
def connect_to_db():
    return sqlite3.connect('telegram_bot.db')  # SQLite database file name

# Function to insert incoming message to inbox table
def insert_inbox_message(user_id, username, message_date, message_text, pesan):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO inbox (user_id, username, message_date, message_text, pesan) VALUES (?, ?, ?, ?, ?)",
                   (user_id, username, message_date, message_text, pesan))
    conn.commit()
    conn.close()

# Function to insert outgoing message to outbox table
def insert_outbox_message(user_id, message_text):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO outbox (user_id, message_text) VALUES (?, ?)", (user_id, message_text))
    conn.commit()
    conn.close()

 
# Handler for '/help' command
@bot.message_handler(commands=['help'])
def help(message):
    user_id = message.from_user.id
    username = message.from_user.username
    message_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    help_text = "Anda dapat menggunakan perintah berikut:\n" \
                "/start - Memulai percakapan\n" \
                "/help - Menampilkan bantuan\n" \
                "Pesan apa pun selain perintah di atas akan dianggap sebagai pesan yang akan diproses oleh bot."

    bot.reply_to(message, help_text)
    insert_inbox_message(user_id, username, message_date, '/help', help_text)
    insert_outbox_message(user_id, help_text)

# Handler for '/start' command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    message_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message_text = "Halo! Selamat datang di bot ini. Silakan mulai dengan mengetikkan pesan apa yang ingin Anda sampaikan."
    pesan = message.text  # Get the user's message
    bot.reply_to(message, message_text)
    insert_inbox_message(user_id, username, message_date, message_text, pesan)
    insert_outbox_message(user_id, message_text)

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
        # Custom responses based on user input
        if message_text.lower() == "hai":
            response = "Hai juga! Ada yang bisa saya bantu?"
        elif message_text.lower() == "terima kasih":
            response = "Sama-sama, senang bisa membantu!"
        else:
            response = "Pesan Anda telah diterima dan akan segera diproses."

    bot.reply_to(message, response)
    insert_inbox_message(user_id, username, message_date, message_text, message_text)
    insert_outbox_message(user_id, response)

# Polling the bot
bot.polling()

# @bot.message_handler(commands=['HaiGanteng'])
# def greet(message):
#     bot.reply_to(message, "Hey ada apa ganteng?")

# bot.polling()

