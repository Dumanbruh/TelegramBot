import telebot
from telebot import types
import mysql.connector
import apiToken

bot = telebot.TeleBot(apiToken.API_KEY)

db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  port="3306",
  database="russiantelegrambot",
  raise_on_warnings = True
)

cursor = db.cursor()


@bot.message_handler(commands = ['start'])

def start_handler(message):
    cid = message.chat.id

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    user_name = message.from_user.first_name
    start_btn = types.InlineKeyboardButton('Начать обучение')
    markup.add(start_btn)

    bot.send_message(cid, "Привет, {}".format(user_name))
    msg = bot.send_message(cid, "Давайте начнем обучение, нажмите кнопки ниже", reply_markup=markup)
    bot.send_message(cid, "Все правила взяты с сайта therules.ru")
    bot.register_next_step_handler(msg, Sections)

def Sections(message) :
    cid = message.chat.id

    cursor.execute("SELECT DISTINCT(section) FROM rules")
    sections = [item[0] for item in cursor.fetchall()]

    section_menu = types.ReplyKeyboardMarkup(True)
    section_menu.add(*[types.InlineKeyboardButton(section) for section in sections])
        
    msg = bot.send_message(cid, 'Пожалуйста, выберите раздел', reply_markup = section_menu)
    bot.register_next_step_handler(msg, FirstStep)

def FirstStep(message) :
    cid = message.chat.id

    query = """SELECT DISTINCT(first_lvl) FROM rules WHERE section LIKE %s"""
    param = (message.text,)

    cursor.execute(query,param)
    first_lvl = [item[0] for item in cursor.fetchall()]

    first_lvl_menu = types.ReplyKeyboardMarkup(True)
    first_lvl_menu.add(*[types.KeyboardButton(name) for name in first_lvl])     
   
    msg = bot.send_message(cid, 'Выберите тему', reply_markup=first_lvl_menu)   
    bot.register_next_step_handler(msg, SecondStep)    


def SecondStep(message) :
    cid = message.chat.id
  
    query = """SELECT second_lvl FROM rules WHERE first_lvl LIKE %s"""
    param = (message.text,)

    cursor.execute(query,param) 
    second_lvl = [item[0] for item in cursor.fetchall()]

    second_lvl_menu = types.ReplyKeyboardMarkup(True)
    second_lvl_menu.add(*[types.KeyboardButton(name) for name in second_lvl])
    second_lvl_menu.add(types.KeyboardButton(text = 'Назад в секцию'))

    msg = bot.send_message(cid, 'Пожалуйста, выберите раздел', reply_markup=second_lvl_menu)
    bot.register_next_step_handler(msg, FinalStep)

def FinalStep(message) :
    cid = message.chat.id

    if message.text == 'Назад в секцию':
        Sections(message)
    else: 
        query = """SELECT content FROM rules WHERE second_lvl = %s"""
        param = (message.text,)

        cursor.execute(query,param)
        final_lvl = cursor.fetchall()
        str_final = ' '.join(map(str,final_lvl)).split('\\r\\n')
        final_lvl_menu = types.ReplyKeyboardMarkup(True)
        final_lvl_menu.add(types.KeyboardButton(text='Назад в секцию'))

        for i in str_final:
            msg = bot.send_message(cid, i.replace("'","").replace("(","").replace(")",""), reply_markup=final_lvl_menu)

        bot.register_next_step_handler(msg, GoBack)



def GoBack(message):
    Sections(message)

    
            


bot.infinity_polling()

