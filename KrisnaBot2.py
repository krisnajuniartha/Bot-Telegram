import os
import telebot
import MySQLdb
# import mysql.connector
from telebot import types
from datetime import datetime
from dotenv import load_dotenv
import time
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

def connect_db():
    return MySQLdb.connect(
        host="localhost", 
        user="root", 
        password="", 
        database="db_botKrisna", 
        port=3306)


def inbox(username, message, date):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO inbox (username, message, date) VALUES (%s, %s, %s)", (username,  message, date))
    conn.commit()
    conn.close()

def outbox(username, message, date):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO outbox (username, message, date) VALUES (%s, %s, %s)", (username,  message, date))
    conn.commit()
    conn.close()

def get_mahasiswa_by_nim(nim):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mahasiswa WHERE nim = %s", (nim,))
    mahasiswa = cursor.fetchone()
    conn.close()
    return mahasiswa

def get_matkul_by_name(matkul_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM matkul WHERE nama LIKE %s", ('%' + matkul_name + '%',))
    matkul = cursor.fetchall()
    conn.close()
    return matkul

# Tambahkan tumpukan global untuk menyimpan menu sebelumnya
menu_stack = []

@bot.message_handler(commands=['cari_mhs'])
def cari_mahasiswa(m):
    answer = "Masukkan NIM mahasiswa yang ingin Anda cari:"
    bot.send_message(m.chat.id, answer)
    username = m.from_user.username
    message = m.text
    date = datetime.now()
    inbox(username, message, date)
    outbox(username, answer, date)
    
    # Tambahkan menu sebelumnya ke tumpukan
    menu_stack.append(handle_show_menu)
    
    bot.register_next_step_handler(m, process_nim_input)

def process_nim_input(m):
    nim = m.text
    mahasiswa = get_mahasiswa_by_nim(nim)
    if mahasiswa:
        info_mahasiswa = f"NIM: {mahasiswa[0]}\nNama: {mahasiswa[1]}"
        bot.send_message(m.chat.id, info_mahasiswa)
    else:
        bot.send_message(m.chat.id, "Maaf, mahasiswa dengan NIM tersebut tidak ditemukan.")

@bot.message_handler(commands=['cari_matkul'])
def cari_matkul(m):
    answer = "Masukkan nama mata kuliah yang ingin Anda cari:"
    bot.send_message(m.chat.id, answer)
    username = m.from_user.username
    message = m.text
    date = datetime.now()
    inbox(username, message, date)
    outbox(username, answer, date)
    
    # Tambahkan menu sebelumnya ke tumpukan
    menu_stack.append(handle_show_menu)
    
    bot.register_next_step_handler(m, process_matkul_name_input)

@bot.message_handler(commands=['back'])
def back_to_previous_menu(m):
    if menu_stack:
        previous_menu = menu_stack.pop()
        previous_menu(m)
    else:
        bot.send_message(m.chat.id, "Anda sudah berada di menu awal.")

@bot.message_handler(commands=['start', 'hello'])
def start(m):
    answer ="Hello what can i do for you?, type /show_menu"
    bot.send_message(m.chat.id, answer)
    username = m.from_user.username
    message = m.text
    date = datetime.now()
    inbox(username, message, date)
    outbox(username, answer, date)

@bot.message_handler(commands=['show_menu'])
def handle_show_menu(m):
    show_menu(m)
    
    # Tambahkan menu sebelumnya ke tumpukan
    menu_stack.append(handle_show_menu)

@bot.message_handler(func=lambda message: True)
def handle_menu(m):
    option = m.text
    data = get_data_from_database(option, m)
    if data is not None:
        bot.send_message(m.chat.id, data)

def show_menu(m):
    options = get_menu_options()
    markup = types.ReplyKeyboardMarkup(row_width=1)
    for option in options:
        option_text = str(option[1]) 
        markup.add(types.KeyboardButton(option_text)) 
    bot.send_message(m.chat.id, "Pilih salah satu menu:", reply_markup=markup)
    username = m.from_user.username
    message = m.text
    date = datetime.now()
    inbox(username, message, date)
    outbox(username, "Show menu", date)


def get_menu_options():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu_options")
    options = cursor.fetchall()
    conn.close()
    return options

def get_data_from_database(option, m):
    if option == "cari_mhs":
        cari_mahasiswa(m)
        return None
    elif option == "cari_matkul":
        cari_matkul(m)
        return None
    else:
        return "Maaf, perintah tidak dikenali."

bot.polling()
