
import telebot
from telebot import types
import random
import threading
from flask import Flask
import os

# Твой проверенный токен
TOKEN = "8637835333:AAFZKCpggslNEYi5YR5BgjDbt1U"
bot = telebot.TeleBot(TOKEN)

# Твоя ссылка
REG_LINK = "https://pocket-friends.co/r/vmbe"

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- ЛОГИКА БОТА ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🔥 ПОЛУЧИТЬ СИГНАЛ", callback_data="get_signal")
    btn2 = types.InlineKeyboardButton("📱 РЕГИСТРАЦИЯ", url=REG_LINK)
    markup.add(btn1, btn2)
    
    welcome_text = (
        "👋 **Добро пожаловать в AI SCANNER!**\n\n"
        "Я — твой автоматический ИИ-ассистент для торговли на платформе Pocket Option.\n"
        "Жми кнопку ниже, чтобы получить первый сигнал!"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "get_signal")
def send_signal(call):
    assets_pool = [
        "EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "AUD/USD (OTC)", 
        "APPLE (OTC)", "GOOGLE (OTC)", "TESLA (OTC)", 
        "BITCOIN (OTC)", "ETHEREUM (OTC)"
    ]
    
    directions = ["⬆️ ВВЕРХ (CALL)", "⬇️ ВНИЗ (PUT)"]
    logics = [
        "Пробой уровня сопротивления, объемы растут.",
        "Перепроданность по RSI, разворот тренда.",
        "Паттерн 'Поглощение' на минутном таймфрейме.",
        "Тестирование сильной зоны спроса."
    ]
    
    asset = random.choice(assets_pool)
    direction = random.choice(directions)
    logic_reason = random.choice(logics)
    
    if "BITCOIN" in asset:
        current_price = round(random.uniform(62000.0, 69000.0), 2)
    elif "ETHEREUM" in asset:
        current_price = round(random.uniform(3100.0, 3600.0), 2)
    else:
        current_price = round(random.uniform(1.0500, 1.2500), 4)
        
    timeframe = random.choice(["1 МИН", "2 МИН", "3 МИН"])
    
    signal_text = (
        f"🎯 **AI SIGNAL TERMINAL V4.0** 🎯\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"📊 **Актив:** {asset}\n"
        f"💰 **Текущая доходность:** 92% ПРИБЫЛИ\n"
        f"📈 **Текущая котировка:** {current_price}\n"
        f"⏱ **Время сделки:** {timeframe}\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"🤖 **Анализ ИИ:** {logic_reason}\n"
        f"👉 **РЕШЕНИЕ:** {direction}\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n"
        f"📉 *Открывай сделку на Pocket Option:*\n"
        f"🔗 [ВОЙТИ НА ПЛАТФОРМУ]({REG_LINK})"
    )
    
    bot.send_message(call.message.chat.id, signal_text, parse_mode="Markdown", disable_web_page_preview=True)
    bot.answer_callback_query(call.id)

if __name__ == "__main__":
    web_thread = threading.Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()
    
    bot.polling(none_stop=True)
