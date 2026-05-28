import telebot
import random
import os
from flask import Flask
from threading import Thread

TOKEN = "8637835333:AAFZKCpggslNEYi5YR5BgjDbt1U"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

# Полный список активов из твоих скриншотов
assets = [
    # Валюты
    {"name": "AUD/CAD OTC", "type": "📈 Валюта"}, {"name": "AUD/CHF OTC", "type": "📈 Валюта"},
    {"name": "BHD/CNY OTC", "type": "📈 Валюта"}, {"name": "CAD/CHF", "type": "📈 Валюта"},
    {"name": "CAD/JPY OTC", "type": "📈 Валюта"}, {"name": "CHF/NOK OTC", "type": "📈 Валюта"},
    {"name": "EUR/AUD", "type": "📈 Валюта"}, {"name": "EUR/CHF OTC", "type": "📈 Валюта"},
    {"name": "EUR/JPY OTC", "type": "📈 Валюта"}, {"name": "EUR/USD OTC", "type": "📈 Валюта"},
    {"name": "GBP/AUD", "type": "📈 Валюта"}, {"name": "GBP/AUD OTC", "type": "📈 Валюта"},
    {"name": "GBP/JPY OTC", "type": "📈 Валюта"}, {"name": "NGN/USD OTC", "type": "📈 Валюта"},
    {"name": "NZD/USD OTC", "type": "📈 Валюта"}, {"name": "OMR/CNY OTC", "type": "📈 Валюта"},
    {"name": "SAR/CNY OTC", "type": "📈 Валюта"}, {"name": "TND/USD OTC", "type": "📈 Валюта"},
    {"name": "UAH/USD OTC", "type": "📈 Валюта"}, {"name": "USD/ARS OTC", "type": "📈 Валюта"},
    # Крипта
    {"name": "Cardano OTC", "type": "💎 Крипто"}, {"name": "Bitcoin OTC", "type": "💎 Крипто"},
    {"name": "Chainlink OTC", "type": "💎 Крипто"}, {"name": "Litecoin OTC", "type": "💎 Крипто"},
    {"name": "Solana OTC", "type": "💎 Крипто"}, {"name": "TRON OTC", "type": "💎 Крипто"},
    # Акции
    {"name": "Apple OTC", "type": "🏢 Акция"}, {"name": "American Express OTC", "type": "🏢 Акция"},
    {"name": "FACEBOOK INC OTC", "type": "🏢 Акция"}, {"name": "Johnson & Johnson OTC", "type": "🏢 Акция"},
    {"name": "McDonald's OTC", "type": "🏢 Акция"}, {"name": "Microsoft OTC", "type": "🏢 Акция"},
    {"name": "AMD OTC", "type": "🏢 Акция"}, {"name": "Alibaba OTC", "type": "🏢 Акция"},
    {"name": "FedEx OTC", "type": "🏢 Акция"}, {"name": "VISA OTC", "type": "🏢 Акция"}
]

allowed_users = [] 

@app.route('/')
def home():
    return "Bot is active"

@bot.message_handler(commands=['signal'])
def signal(message):
    if message.chat.id in allowed_users:
        item = random.choice(assets)
        direction = random.choice(["ВВЕРХ 🟢", "ВНИЗ 🔴"])
        prob = random.randint(87, 99)
        sig_id = random.randint(1000, 9999)
        
        msg = (
            f"🤖 **AI SIGNAL GENERATOR**\n"
            f"🆔 ID: #{sig_id}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔹 АКТИВ: `{item['name']}`\n"
            f"📊 ТИП: {item['type']}\n"
            f"💰 ВЫПЛАТА: *92%*\n"
            f"📈 ВЕРОЯТНОСТЬ: *{prob}%*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎯 РЕШЕНИЕ: {direction}\n"
            f"⏱ ЭКСПИРАЦИЯ: 3-5 мин\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "⛔️ **ДОСТУП ОГРАНИЧЕН**\nЗарегистрируйтесь по ссылке из /start и пришлите ID.")

# ... (остальной функционал бота оставляем как был)

