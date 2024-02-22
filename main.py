import telebot
from telebot import types
import time
import sqlite3
import asyncio

bot = telebot.TeleBot("")
mes_id = 1

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    global mes_id
    data = call.data
    bot.delete_message(call.message.chat.id, mes_id)
    if data == "add_to_group":
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        btn = types.InlineKeyboardButton(text="Меню", callback_data="menu")
        btn1 = types.InlineKeyboardButton(text="Команды для управления", callback_data="commands")
        keyboard.add(btn, btn1)
        mes_id = bot.send_message(call.message.chat.id, "1. Добавь меня в группу\n2. Выдай мне права для блокировки пользователей", reply_markup=keyboard).id
    if data == "commands":
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        btn = types.InlineKeyboardButton(text="Меню", callback_data="menu")
        btn1 = types.InlineKeyboardButton(text="Добавить в группу", callback_data="add_to_group")
        keyboard.add(btn, btn1)
        mes_id = bot.send_message(call.message.chat.id, "/mute - замутить на 1 час\n вместо 1 напишите свое время в часах\n/unmute - размутить/block - навсегда запретить писать\n\nЧтобы замутить или удалть пользователя напишите одну из команд в ответ на его сообщение", reply_markup=keyboard).id
    if data == "menu":
        start(call.message)

@bot.message_handler(commands=['start', 'help'])
def start(message):
    global mes_id
    db = sqlite3.connect("db.db")
    cursor = db.cursor()

    if message.chat.type == 'private':
        if cursor.execute(f"SELECT * FROM users WHERE id='{message.chat.id}'").fetchone() is None:
            cursor.execute(f"INSERT INTO users (id) VALUES ('{message.chat.id}')")
            db.commit()
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        btn = types.InlineKeyboardButton(text="Добавить в группу", callback_data="add_to_group")
        btn1 = types.InlineKeyboardButton(text="Команды для управления", callback_data="commands")
        btn2 = types.InlineKeyboardButton(text="Тех. поддержка", url="https://t.me/raid_kasik")
        keyboard.add(btn, btn1, btn2)
        mes_id = bot.send_message(message.chat.id, "Привет!\nЭтот бот поможет тебе в управление твоей группы\n\nВладелец: @raid_kasik\nАдмин: @Chotkiy_potsan", reply_markup=keyboard).id


async def mute_h(time_mute, user_id, chat_id):
    try:
        bot.restrict_chat_member(chat_id, user_id)
        bot.send_message(chat_id, f"✅Пользователь {user_id} заблокирован на {float(time_mute)}h")
        time.sleep(float(time_mute) * 60 * 60)
        bot.promote_chat_member(chat_id, user_id)
    except: bot.send_message(chat_id, "❌Укажите время")

async def mute_d(time_mute, user_id, chat_id):
    try:
        bot.restrict_chat_member(chat_id, user_id)
        bot.send_message(chat_id, f"✅Пользователь {user_id} заблокирован на {float(time_mute)}d")
        time.sleep(float(time_mute) * 60 * 60 * 24)
        bot.promote_chat_member(chat_id, user_id)
    except: bot.send_message(chat_id, "❌Укажите время")


@bot.message_handler(commands=['mute', 'unmute', 'block'])
def com(message):
    if message.chat.type != 'private' and (bot.get_chat_member(message.chat.id, message.chat.id).status == "admin" or bot.get_chat_member(message.chat.id, message.chat.id).status == "creator"):
        if "/block" in message.text:
            bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            bot.send_message(message.chat.id, f"✅Пользователь {message.reply_to_message.from_user.id} заблокирован")

        if "/mute" in message.text:
            t = message.text.split(" ")[-1]
            if "h" in message.text:
                asyncio.run(mute_h(t, message.reply_to_message.from_user.id.replace("h", ""), message.chat.id))
            elif "d" in message.text:
                asyncio.run(mute_d(t, message.reply_to_message.from_user.id.replace("d", ""), message.chat.id))

        if "/unmute" in message.text:
            bot.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            bot.send_message(message.chat.id, f"✅Пользователь {message.reply_to_message.from_user.id} разблокирован")

@bot.message_handler(commands=['del', 'add'])
def admin(message):
    db = sqlite3.connect("db.db")
    cursor = db.cursor()

    if cursor.execute(f"SELECT * FROM admin WHERE id='{message.chat.id}'").fetchone() is not None:
        if "add" in message.text:
            try:
                uid = message.text.split(' ')[-1]
                cursor.execute(f"INSERT INTO admin (id) VALUES ('{uid}')")
                db.commit()
                bot.send_message(message.chat.id, "✅Успешно!")
            except Exception as ex:
                bot.send_message(message.chat.id, f"❌{ex}")

        if "del" in message.text:
            try:
                uid = message.text.split(' ')[-1]
                cursor.execute(f"DELETE FROM admin WHERE id='{uid}'")
                db.commit()
                bot.send_message(message.chat.id, "✅Успешно!")
            except Exception as ex:
                bot.send_message(message.chat.id, f"❌{ex}")
bot.polling()

