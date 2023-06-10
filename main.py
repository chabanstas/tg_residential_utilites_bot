import telebot
import config
import sqlite3
from telebot import types
import texts
import db

bot = telebot.TeleBot(config.TOKEN)

db.create_tables()

@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    commands = [
        types.InlineKeyboardButton('📝Мої особові рахунки', callback_data='my_bills'),
        types.InlineKeyboardButton('📊Передати показники лічильника', callback_data='transfer_counter_readings'),
        types.InlineKeyboardButton('💳Сплатити', callback_data='pay'),
        types.InlineKeyboardButton('📞Зворотній звязок', callback_data='feedback'),
        types.InlineKeyboardButton('❕Корисна інформація', callback_data='addition'),
        types.InlineKeyboardButton('ℹ️ Про бот', callback_data='adout_bot')
    ]
    markup.add(*commands)
    bot.send_message(message.chat.id, "✋Вітаю! Це Єдиний розрахунковий центр по житлово-комунальним послугам.\n⬇️Доступні команди:", reply_markup=markup)
    
@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    if call.data == 'my_bills':
        my_bills_handler(call.message)
    elif call.data == 'adout_bot':
        adout_bot_handler(call.message)
    elif call.data == 'to_main':
        start_handler(call.message)
    elif call.data == 'add_bill':
        add_bill_handler(call.message)
    elif call.data == 'delete_bill':
        delete_bill_handler(call.message)
    elif call.data.startswith('confirm_delete_'):
        confirm_delete_handler(call.message, call.data.split('_')[2])
    elif call.data.startswith('execute_delete_'):
        execute_delete_handler(call.message, call.data.split('_')[2])
    elif call.data.startswith('view_bill_'):
        view_bill_handler(call.message, call.data.split('_')[2])
    elif call.data == 'transfer_counter_readings':
        transfer_counter_readings_handler(call.message)
    elif call.data.startswith('zones_bill_'):
        select_zones_bill_handler(call.message, call.data.split('_')[2])
    elif call.data.startswith('zone1_'):
        zone1_handler(call.message, call.data.split('_')[1])
    elif call.data.startswith('zone2_'):
        zone2_handler(call.message, call.data.split('_')[1])
    elif call.data == 'pay':
        pay(call.message)
    elif call.data.startswith('pay_bill_'):
        pay_bill_handler(call.message, call.data.split('_')[2])
    elif call.data == 'feedback':
        feedback_handler(call.message)
    elif call.data == 'contacts':
        contacts_handler(call.message)
    elif call.data == 'message':
        message_user_handler(call.message)
    elif call.data == 'addition':
        addition_handler(call.message)
    elif call.data == 'tariffs':
        tariffs_handler(call.message)
    elif call.data == 'links':
        links_handler(call.message)
    elif call.data.startswith('pay_method_handler_'):
        pay_method_handler(call.message, call.data.split('_')[3])
    elif call.data.startswith('crypt_pay'):
        crypt_pay_handler(call.message)
    elif call.data.startswith('payment_systems_pay'):
        payment_systems_pay_handler(call.message)
    elif call.data.startswith('paid_'):
        paid_handler(call.message, call.data.split('_')[1])
    elif call.data.startswith('gas'):
        add_type_bill_handler(call.message, "Газ")
    elif call.data.startswith('gas_delivery'):
        add_type_bill_handler(call.message, "Доставка газу")
    elif call.data.startswith('electricity'):
        add_type_bill_handler(call.message, "Електроенергія")
    elif call.data.startswith('water'):
        add_type_bill_handler(call.message, "Водопостачання")
    elif call.data.startswith('drainage'):
        add_type_bill_handler(call.message, "Водовідведення")
    elif call.data.startswith('hot_water'):
        add_type_bill_handler(call.message, "Постачання гарячої води")
    elif call.data.startswith('rubbish'):
        add_type_bill_handler(call.message, "Вивіз сміття")
    elif call.data.startswith('internet'):
        add_type_bill_handler(call.message, "Інтернет")
    elif call.data.startswith('view_photo_handler_'):
        view_photo_handler(call.message, call.data.split('_')[3])
    

def adout_bot_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    command = types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    markup.add(command)
    bot.send_message(message.chat.id, texts.about_bot, reply_markup=markup)

def my_bills_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    commands = [
        types.InlineKeyboardButton('➕Додати особовий рахунок', callback_data='add_bill'),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    bills = get_bills()
    if len(bills) >= 2:
        commands.insert(0, types.InlineKeyboardButton("➖Видалити рахунок", callback_data='delete_bill'))
    for bill in bills:
        commands.insert(0, types.InlineKeyboardButton(bill, callback_data='view_bill_{}'.format(bill)))
        
    markup.add(*commands)   
    bot.send_message(message.chat.id, '⬇️Оберіть особовий рахунок або додайте новий:', reply_markup=markup)
    
def add_bill_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    commands = [
        types.InlineKeyboardButton('🔥Газ', callback_data='gas'),
        types.InlineKeyboardButton('🔥Доставка газу', callback_data='gas_delivery'),
        types.InlineKeyboardButton('💡Електроенергія', callback_data='electricity'),
        types.InlineKeyboardButton('💧Водопостачання', callback_data='water'),
        types.InlineKeyboardButton('💧Водовідведення', callback_data='drainage'),
        types.InlineKeyboardButton('🌡️Постачання гарячої води', callback_data='hot_water'),
        types.InlineKeyboardButton('🗑️Вивіз сміття', callback_data='rubbish'),
        types.InlineKeyboardButton('🌐Інтернет', callback_data='internet'),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
        ]
    markup.add(*commands)
    bot.send_message(message.chat.id, "⬇️Виберіть тип послуги:", reply_markup=markup)

def add_type_bill_handler(message, service_type):
    markup = types.InlineKeyboardMarkup(row_width=1)
    command = types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    markup.add(command)
    bot.send_message(message.chat.id, f"⌨️Введіть номер Вашого особового рахунку (номер складається з 10 цифр) для {service_type}:", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: process_add_bill(msg, service_type))

def process_add_bill(message, service_type):
    personal_account = message.text
    if check_valid_personal_account(message, personal_account):
        return
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO bills (personal_account, type, new_zone1, new_zone2, old_zone1, old_zone2, paid) VALUES (?, ?, ?, ?, ?, ?, ?)', (personal_account, service_type, 0, 0, 0, 0, False))
    conn.commit()
    cursor.close()
    conn.close()
    bot.send_message(message.chat.id, "✅Особовий рахунок додано!")
    start_handler(message)
   
def delete_bill_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    commands = [
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    bills = get_bills()
    for bill in bills:
        commands.insert(0, types.InlineKeyboardButton(bill, callback_data='confirm_delete_{}'.format(bill)))

    markup.add(*commands)
    bot.send_message(message.chat.id, '⬇️Оберіть рахунок для видалення:', reply_markup=markup)

def confirm_delete_handler(message, bill):
    markup = types.InlineKeyboardMarkup(row_width=1)
    commands = [
        types.InlineKeyboardButton('✔️Підтвердити видалення', callback_data='execute_delete_{}'.format(bill)),
        types.InlineKeyboardButton('✖️Скасувати', callback_data='my_bills')
    ]
    markup.add(*commands)
    bot.send_message(message.chat.id, f"⁉️Ви впевнені, що бажаєте видалити рахунок {bill}?", reply_markup=markup)
   
def execute_delete_handler(call, bill):
    delete_bill(bill)
    bot.send_message(call.chat.id, f"✅Рахунок {bill} був успішно видалений.")
    my_bills_handler(call)

def delete_bill(bill):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM bills WHERE personal_account = ?', (bill,))
    conn.commit()
    cursor.close()
    conn.close()
 
def get_bills():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT personal_account FROM bills''')
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return [row[0] for row in result] 

def transfer_counter_readings_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    commands = [
        types.InlineKeyboardButton('➕Додати особовий рахунок', callback_data='add_bill'),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    bills = get_bills()
    if len(bills) >= 2:
        commands.insert(0, types.InlineKeyboardButton("➖Видалити рахунок", callback_data='delete_bill'))
    for bill in bills:
        commands.insert(0, types.InlineKeyboardButton(bill, callback_data='zones_bill_{}'.format(bill)))
    
    markup.add(*commands)   
    bot.send_message(message.chat.id, '⬇️Оберіть особовий рахунок для передачі показників:', reply_markup=markup)

def view_bill_handler(message, bill):
    address = get_address(bill)
    sum = calculate_payment_amount(bill)
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT new_zone1, new_zone2, old_zone1, old_zone2, type, paid FROM bills WHERE personal_account = ?', (bill,))
    result = cursor.fetchone()
    current_rate1 = result[0] if result else 0
    past_rate1 = result[2] if result else 0
    account_type = result[4]
    paid = result[5]
    cursor.close()
    conn.close()
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    commands = [
        types.InlineKeyboardButton('📷Переглянути фото', callback_data='view_photo_handler_{}'.format(bill)),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    markup.add(*commands)
    if paid:
        text_paid = '✅Сплачено'
    else:
        text_paid = f'❗️Потрібно сплатити: {sum} грн.'
    text = f"📄Рахунок {account_type} {bill} зареєстровано за адресою:\n\n{address}\n🔒Статус:\n{text_paid}\n\n🔢Рахункові показники:\n🔼Поточний = {current_rate1}\n🔽Попередній = {past_rate1}"
    bot.send_message(message.chat.id, text, reply_markup=markup)
    
def select_zones_bill_handler(message, bill):
    markup = types.InlineKeyboardMarkup(row_width=1)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT type FROM bills WHERE personal_account = ?', (bill,))
    result = cursor.fetchone()
    account_type = result[0] if result else None
    
    address = get_address(bill)
    
    if account_type == "Газ":
        commands  = [
        types.InlineKeyboardButton('🔥Лічильник газовий', callback_data='zone1_{}'.format(bill)),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    elif account_type == "Доставка газу":
        commands  = [
        types.InlineKeyboardButton('🔥Підтвердити вибір: Доставка газу', callback_data='zone1_{}'.format(bill)),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    elif account_type == "Електроенергія":
        commands  = [
        types.InlineKeyboardButton('1️⃣1 зона', callback_data='zone1_{}'.format(bill)),
        types.InlineKeyboardButton('2️⃣2 зони', callback_data='zone2_{}'.format(bill)),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    elif account_type == "Водопостачання":
        commands  = [
        types.InlineKeyboardButton('💧Підтвердити вибір: Водопостачання', callback_data='zone1_{}'.format(bill)),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    elif account_type == "Водовідведення":
        commands  = [
        types.InlineKeyboardButton('💧Підтвердити вибір: Водовідведення', callback_data='zone1_{}'.format(bill)),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    elif account_type == "Постачання гарячої води":
        commands  = [
        types.InlineKeyboardButton('🌡️Підтвердити вибір: Постачання гарячої води', callback_data='zone1_{}'.format(bill)),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    elif account_type == "Вивіз сміття":
        commands  = [
        types.InlineKeyboardButton('🗑️Підтвердити вибір: Вивіз сміття', callback_data='zone1_{}'.format(bill)),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    elif account_type == "Інтернет":
        commands  = [
        types.InlineKeyboardButton('🌐Підтвердити вибір: Інтернет', callback_data='zone1_{}'.format(bill)),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    markup.add(*commands)
    texts = [f"📄Рахунок {bill}\nЗареєстровано за адресою:\n\n{address}", "⬇️Оберіть відповідний варіант:"]
    bot.send_message(message.chat.id, texts[0])
    bot.send_message(message.chat.id, texts[1], reply_markup=markup)

def get_address(bill):
    db.generate_test_data(1, bill)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM addresses WHERE personal_account = ?', (bill,))
    rows = cursor.fetchall()

    response = ""
    for row in rows:
        response += f"📍Місто: {row[2]}, вулиця: {row[3]}, будинок: {row[4]}, підїзд: {row[5]}, квартира: {row[6]}\n"

    cursor.close()
    conn.close()

    return response   
 
def zone1_handler(message, bill):
    bot.send_message(message.chat.id, "⌨️Введіть показання (всі цифри до коми):")
    bot.register_next_step_handler(message, process_zone1_handler, bill)

def process_zone1_handler(message, bill):
    zone1 = message.text
    if not check_input_validity(zone1):
        bot.send_message(message.chat.id, "❌Введені дані некоректні. Будь ласка, введіть лише числове значення.")
        start_handler(message)
        return
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT new_zone1, old_zone1 FROM bills WHERE personal_account = ?', (bill,))
    result = cursor.fetchone()
    current_zone1 = result[0] if result else 0
    old_zone1 = result[1] if result else 0
    
    if current_zone1 != 0:
        cursor.execute('UPDATE bills SET old_zone1 = ?, paid = ? WHERE personal_account = ?', (current_zone1, False, bill))
    
    if current_zone1 < old_zone1:
        bot.send_message(message.chat.id, "❌Значення попереднього показника (1 зона) не може бути меншим за поточне значення.")
        start_handler(message)
        return
   
    cursor.execute('UPDATE bills SET new_zone1 = ?, paid = ? WHERE personal_account = ?', (zone1, False, bill))
    conn.commit()
    cursor.close()
    conn.close()

    bot.send_message(message.chat.id, "✅Показник додано!\n📷Тепер сфотографуйте лічильник, щоб було видно цифри до коми:")
    bot.register_next_step_handler(message, photo_handler, bill)
 
def photo_handler(message, bill):
    photo = message.photo[-1]
    file_id = photo.file_id

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        types.KeyboardButton('✅ Підтверджую'),
        types.KeyboardButton('❌ Відмінити')
        ]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "Підтвердіть, що фотографія була зроблена належним чином та не було застосовано графічних редакторів:", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: save_photo(msg, bill, file_id))

def save_photo(message, bill, file_id):
    personal_account = message.text

    if personal_account == '❌ Відмінити':
        bot.send_message(message.chat.id, "❌ Завантаження фотографії скасовано.")
        start_handler(message)
        return

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO photos (personal_account, file_id) VALUES (?, ?)', (bill, file_id))
    conn.commit()
    cursor.close()
    conn.close()

    bot.send_message(message.chat.id, "✅ Фотографію збережено успішно!")
    start_handler(message)

def view_photo_handler(message, bill):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT file_id FROM photos WHERE personal_account = ?', (bill,))
    result = cursor.fetchone()
    if result:
        file_id = result[0]
        bot.send_photo(message.chat.id, file_id)
    else:
        bot.send_message(message.chat.id, "Фотографія для даного рахунку не знайдена.")
    cursor.close()
    conn.close()
   
def zone2_handler(message, bill):
    bot.send_message(message.chat.id, f"2️⃣Ви вибрали зонність свого лічильнику: 2 зони")
    bot.send_message(message.chat.id, "⌨️Введіть показання: ☀️ДЕНЬ пробіл 🌙НІЧ (всі цифри до коми).")
    bot.register_next_step_handler(message, process_zone2_handler, bill)

def process_zone2_handler(message, bill):
    text = message.text
    words = text.split()
    for word in words:
        if not check_input_validity(word):
            bot.send_message(message.chat.id, "❌Введені дані некоректні. Будь ласка, введіть лише числове значення.")
            start_handler(message)
            return
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT new_zone1, new_zone2, old_zone1, old_zone2 FROM bills WHERE personal_account = ?', (bill,))
    result = cursor.fetchone()
    current_zone1 = result[0] if result else 0
    current_zone2 = result[1] if result else 0
    old_zone1 = result[2] if result else 0
    old_zone2 = result[3] if result else 0
    
    if current_zone1 != 0:
        cursor.execute('UPDATE bills SET old_zone1 = ?, paid = ? WHERE personal_account = ?', (current_zone1, False, bill))
    
    if current_zone2 != 0:
        cursor.execute('UPDATE bills SET old_zone2 = ?, paid = ? WHERE personal_account = ?', (current_zone2, False, bill))
    
    if current_zone1 < old_zone1:
        bot.send_message(message.chat.id, "❌Значення попереднього показника (1 зона) не може бути більшим за нове значення.")
        start_handler(message)
        return
    
    if current_zone2 < old_zone2:
        bot.send_message(message.chat.id, "❌Значення попереднього показника (2 зона) не може бути більшим за нове значення.")
        start_handler(message)
        return
    
    cursor.execute('UPDATE bills SET new_zone1 = ?, paid = ? WHERE personal_account = ?', (words[0], False, bill))
    cursor.execute('UPDATE bills SET new_zone2 = ?, paid = ? WHERE personal_account = ?', (words[1], False, bill))
    conn.commit()
    cursor.close()
    conn.close()

    bot.send_message(message.chat.id, "✅Показник (2 зони) додано!")
    start_handler(message)
 
def check_input_validity(text):
    if not text.isdigit():
        return False
    return True   

def pay(message): 
    markup = types.InlineKeyboardMarkup(row_width=1)
    commands = [
        types.InlineKeyboardButton('➕Додати особовий рахунок', callback_data='add_bill'),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    bills = get_bills()
    if len(bills) >= 2:
        commands.insert(0, types.InlineKeyboardButton("➖Видалити рахунок", callback_data='delete_bill'))
    for bill in bills:
        commands.insert(0, types.InlineKeyboardButton(bill, callback_data='pay_bill_{}'.format(bill)))
    
    markup.add(*commands)   
    bot.send_message(message.chat.id, 'Оберіть особовий рахунок для сплати:', reply_markup=markup)   
      
def pay_bill_handler(message, bill):
    address = get_address(bill)
    sum = calculate_payment_amount(bill)
    markup = types.InlineKeyboardMarkup(row_width=1)
    commands = [
        types.InlineKeyboardButton(f'💰Сплатити {sum}', callback_data='pay_method_handler_{}'.format(bill)),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    markup.add(*commands)

    bot.send_message(message.chat.id,  f"📄Рахунок {bill} зареєстровано за адресою:\n\n{address}", reply_markup=markup)
 
def pay_method_handler(message, bill):
    markup = types.InlineKeyboardMarkup(row_width=1)
    commands = [
        types.InlineKeyboardButton(f'💳Карткова оплата', url="https://buy.stripe.com/test_3cs6ru3zwfbvgKcbII"),
        types.InlineKeyboardButton(f'💰Оплата через платіжні системи', callback_data='payment_systems_pay'),
        types.InlineKeyboardButton(f'🌐Оплата за допомогою криптовалют', callback_data='crypt_pay'),
        types.InlineKeyboardButton(f'✅Позначити рахунок {bill} сплаченим', callback_data='paid_{}'.format(bill)),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    markup.add(*commands)
    
    bot.send_message(message.chat.id, "⬇️Виберіть спосіб оплати:", reply_markup=markup)
    
def calculate_payment_amount(bill):
    gas_rate = 7.96
    gas_delivery_rate = 1.79
    wather_rate = 8.94
    drainage_rate = 3.06
    day_rate = 1.44
    more_day_rate = 1.68
    night_rate = day_rate/2
    hot_wather = 69.62
    garbage_removal_rate = 36.11
    internet_rate = 90
    sum = 0
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT new_zone1, new_zone2, old_zone1, old_zone2, type FROM bills WHERE personal_account = ?', (bill,))
    result = cursor.fetchone()
    current_rate1 = result[0] if result else 0
    past_rate1 = result[1] if result else 0
    current_rate2 = result[2] if result else 0
    past_rate2 = result[3] if result else 0
    account_type = result[4]
    cursor.close()
    conn.close()
    
    if account_type == "Газ":
        if (current_rate1 == 0 and current_rate2 == 0) or current_rate2 == 0:
            sum = 10 * gas_rate
        else:
            sum = (current_rate1 - current_rate2) * gas_rate      
    elif account_type == "Доставка газу":
        sum = 10 * gas_delivery_rate
    elif account_type == "Електроенергія":
        if current_rate1 and current_rate2 == 0 and current_rate1 == 0:
            day_amount = 0
        elif current_rate2 == 0:
            day_amount = 160 * 1.44
        else:
            day_amount = (current_rate1 - current_rate2)
            if day_amount > 250:
                day_amount = day_amount * more_day_rate
            else:
                day_amount = day_amount * day_rate
        
        if past_rate1 and past_rate2 == 0 and past_rate1 == 0:
            night_amount = 0
        elif past_rate1 != 0 and past_rate2 == 0:
            night_amount = 80 * 0.72
        else:
            night_amount = (past_rate1 - past_rate2) * night_rate
        sum = day_amount + night_amount
    elif account_type == "Водопостачання":
        if (current_rate1 == 0 and current_rate2 == 0) or current_rate1 != 0:
            sum = 10 * wather_rate
        else:
            sum = (current_rate1 - current_rate2) * wather_rate 
    elif account_type == "Водовідведення":
        sum = 10 * drainage_rate
    elif account_type == "Постачання гарячої води":
        if (current_rate1 == 0 and current_rate2 == 0) or current_rate1 != 0:
            sum = 10 * hot_wather
        else:
            sum = (current_rate1 - current_rate2) * hot_wather
    elif account_type == "Вивіз сміття":
        sum = 1 * garbage_removal_rate
    elif account_type == "Інтернет":
        sum = 1 * internet_rate
    else:
        sum = -1
       
    sum = round(sum, 2)
    
    return sum
 
def feedback_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    commands = [
        types.InlineKeyboardButton('➖Написати повідомлення', callback_data='message'),
        types.InlineKeyboardButton('📞Контакти', callback_data='contacts'),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    markup.add(*commands)
    bot.send_message(message.chat.id, "Вітаю! Це Єдиний розрахунковий центр по житлово-комунальним послугам. Доступні команди:", reply_markup=markup)

def contacts_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    command = types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    markup.add(command)
    email = "test"
    phone = "test"
    bot.send_message(message.chat.id, f"↔️ Зворотній зв'язок:\n\n📧 Електронна пошта: {email}\n📞 Телефон: {phone}", reply_markup=markup)

def message_user_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    command = types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    markup.add(command)
    bot.send_message(message.chat.id, "➖Напишіть повідомлення:", reply_markup=markup)
    bot.register_next_step_handler(message, process_message_user_handler)
    
def process_message_user_handler(message):
    bot.send_message(message.chat.id, "✅Ваше повідомлення надіслано!")
    start_handler(message)

def addition_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    commands = [
        types.InlineKeyboardButton(f'💰Тарифи', callback_data='tariffs'),
        types.InlineKeyboardButton(f'🔗Посилання, які варто відвідати', callback_data='links'),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    markup.add(*commands)
    
    bot.send_message(message.chat.id, '📋Оберіть наступні дії:', reply_markup=markup)

def tariffs_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    commands = [
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    markup.add(*commands)
    tariffs = [
        "🔥Газ і розподіл (доставка) газу:\n🔹 7,96 грн. (з ПДВ) за 1 м³\n🔹 1,79 грн. за 1 м³\n\n",
        "💡Електроенергія:\n🔹 до 250 кВт⋅год (включно) - 1,44 грн. (з ПДВ) за 1 кВт⋅год\n🔹 понад 250 кВт⋅год — 1,68 грн. (з ПДВ) за 1 кВт⋅год\n\n",
        "💧Водопостачання та водовідведення:\n🔹 від 8,94 до 39,42 грн. за 1 м³, з ПДВ\n🔹 від 3,06 до 40,51 грн. за 1 м³, з ПДВ",
        "🌡️Постачання гарячої води:\n🔹 від 69,62 до 110,05 грн. за 1 м³, з ПДВ",
        "🗑️Вивіз сміття\n🔹 36,11 грн",
        "🌐Інтернет:\n🔹 від 90 до 1000 грн/міс"
    ]
    for tariff in tariffs:
        bot.send_message(message.chat.id, tariff)
    bot.send_message(message.chat.id, '⬇️Оберіть наступні дії:', reply_markup=markup)

def links_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    commands = [
        types.InlineKeyboardButton(text="🔹Права споживачів житлово-комунальних послуг та їх захист", url="https://wiki.legalaid.gov.ua/index.php/%D0%9F%D1%80%D0%B0%D0%B2%D0%B0_%D1%81%D0%BF%D0%BE%D0%B6%D0%B8%D0%B2%D0%B0%D1%87%D1%96%D0%B2_%D0%B6%D0%B8%D1%82%D0%BB%D0%BE%D0%B2%D0%BE-%D0%BA%D0%BE%D0%BC%D1%83%D0%BD%D0%B0%D0%BB%D1%8C%D0%BD%D0%B8%D1%85_%D0%BF%D0%BE%D1%81%D0%BB%D1%83%D0%B3_%D1%82%D0%B0_%D1%97%D1%85_%D0%B7%D0%B0%D1%85%D0%B8%D1%81%D1%82"),
        types.InlineKeyboardButton(text="🔹Комунальні тарифи", url="https://index.minfin.com.ua/ua/tariff/"),
        types.InlineKeyboardButton(text="🔹Як правильно подати показник газового лічильника", url="https://zaxid.net/yak_pravilno_podati_pokaznik_gazovogo_lichilnika_i_navishho_tse_robiti_n1551437"),
        types.InlineKeyboardButton(text="🔹Як правильно подати показник електролічильника", url="https://loe.lviv.ua/ua/pokaz_pobut"),
        types.InlineKeyboardButton(text="🔹ЦЕНТР КОМУНАЛЬНОГО СЕРВІСУ", url="https://cks.com.ua/"),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    markup.add(*commands)
    bot.send_message(message.chat.id, "🔗Посилання, які варто відвідати:", reply_markup=markup)

def crypt_pay_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    command = types.InlineKeyboardButton('⬅️Методи оплати', callback_data='pay_method_handler_')
    markup.add(command)
    bot.send_message(message.chat.id, "⭕️Перепрошую, даний метод оплати за допомогою криптовалюти тимчасово недоступний.\n\n👨‍💻Наші спеціалісти вже працюють над проблемою.\n\n⬇️Оберіть наступну дію:", reply_markup=markup)

def payment_systems_pay_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    command = types.InlineKeyboardButton('⬅️Методи оплати', callback_data='pay_method_handler_')
    markup.add(command)
    bot.send_message(message.chat.id, "⭕️Упс.. Щось пішло не так. Виникла помилка.\n\n👨‍💻Наші спеціалісти вже працюють над проблемою.\n\n⬇️Оберіть наступну дію:", reply_markup=markup)

def paid_handler(message, bill):
    address = get_address(bill)
    markup = types.InlineKeyboardMarkup(row_width=1)
    commands = [
        types.InlineKeyboardButton('📞Зворотній звязок', callback_data='feedback'),
        types.InlineKeyboardButton('🏠На головну', callback_data='to_main')
    ]
    markup.add(*commands)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE bills SET paid = ? WHERE personal_account = ?', (True, bill))
    conn.commit()
    cursor.close()
    conn.close()
    bot.send_message(message.chat.id, f"📄Рахунок {bill} було сплачено успішно!✅\n\nЗа адресою:\n{address} прийде квитанція про оплату.\n\nЗалишились питання - напишіть адміністратору або зателефонуйте за телефоном⬇️", reply_markup=markup)

def check_valid_personal_account(message, personal_account):
    if not check_input_validity(personal_account) or len(personal_account) != 10:
        bot.send_message(message.chat.id, "❌ Введені дані некоректні. Будь ласка, введіть лише числове значення довжиною 10 символів.")
        start_handler(message)
        return True
  
@bot.message_handler(commands=['cdb'])
def view_all_users(message):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bills')
    rows = cursor.fetchall()

    if len(rows) == 0:
        bot.send_message(message.chat.id, "База даних користувачів порожня.")
    else:
        response = "Усі користувачі:\n"
        for row in rows:
            response += f"ID: {row[0]}, о/р: {row[1]}, тип: {row[2]}, new zone1: {row[3]}, new zone2: {row[4]}, old zone1: {row[5]}, old zone2: {row[6]}, paid:{row[7]}\n"
        bot.send_message(message.chat.id, response)

    cursor.close()
    conn.close()
@bot.message_handler(commands=['cdb1'])
def get_all_addresses(message):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM addresses')
    rows = cursor.fetchall()
    if len(rows) == 0:
        bot.send_message(message.chat.id, "База даних користувачів порожня.")
    else:
        response = "Усі адреси:\n"
        for row in rows:
            response += f"ID: {row[0]}, о/р: {row[1]}, місто: {row[2]}, вулиця: {row[3]}, будинок: {row[4]}, підїзд: {row[5]}, квартира: {row[6]}\n"
        bot.send_message(message.chat.id, response)
    cursor.close()
    conn.close()
        
bot.polling(none_stop=True)