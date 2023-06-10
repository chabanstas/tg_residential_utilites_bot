import telebot
import config
import sqlite3
import random

bot = telebot.TeleBot(config.TOKEN)

def create_tables():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS bills (id INTEGER PRIMARY KEY AUTOINCREMENT, personal_account TEXT, 
                   type TEXT, new_zone1 REAL, new_zone2 REAL, old_zone1 REAL, old_zone2 REAL, paid BOOLEAN)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS addresses (id INTEGER PRIMARY KEY AUTOINCREMENT, personal_account TEXT, 
                   settlement TEXT, street TEXT, house_number TEXT, entrance_number TEXT, apartment_number TEXT)''')
    cursor.execute('CREATE TABLE IF NOT EXISTS photos (id INTEGER PRIMARY KEY AUTOINCREMENT, personal_account TEXT, file_id TEXT)')
    conn.commit()
    cursor.close()
    conn.close()
    
def generate_test_data(num_addresses, bill):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM addresses WHERE personal_account = ?', (bill,))
    result = cursor.fetchone()
    if result:
        return
    for i in range(num_addresses):
        personal_account = bill
        settlement = 'Київ'
        street = 'Миру'
        house_number = random.randint(1, 300)
        entrance_number = random.randint(1, 10)
        apartment_number = random.randint(1, 100)

        cursor.execute('INSERT INTO addresses (personal_account, settlement, street, house_number, entrance_number, apartment_number) VALUES (?, ?, ?, ?, ?, ?)',
                       (personal_account, settlement, street, house_number, entrance_number, apartment_number))

    conn.commit()
    cursor.close()
    conn.close()