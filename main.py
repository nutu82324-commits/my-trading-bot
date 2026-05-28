
import telebot
from telebot import types
import random
import os
from flask import Flask
from threading import Thread

TOKEN = "8637835333:AAFZKCpggslNEYi5YR5BgjDbt1UtxW_D4CI"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# Запускаем веб-сервер в отдельном потоке
Thread(target=run).start()

# Логика бота
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Бот готов! Жми /signal для получения сигнала.")

@bot.message_handler(commands=['signal'])
def get_signal(message):
    bot.send_message(message.chat.id, f"🎯 Актив: EUR/USD | 📈 Решение: ВВЕРХ")

bot.polling(none_stop=True)
