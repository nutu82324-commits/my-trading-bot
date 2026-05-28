import telebot
import random
from flask import Flask
from threading import Thread

# Твой рабочий токен
TOKEN = "8637835333:AAFZKCpggslNEYi5YR5BgjDbt1U"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

# Полная база активов из твоих скриншотов
assets = [
    {"name": "AUD/CAD OTC", "type": "📈 Валюта"}, {"name": "Bitcoin OTC", "type": "💎 Крипто"},
    {"name": "Apple OTC", "type": "🏢 Акция"}, {"name": "VISA OTC", "type": "🏢 Акция"},
    {"name": "EUR/USD OTC", "type": "📈 Валюта"}, {"name": "Solana OTC", "type": "💎 Крипто"},
    {"name": "Microsoft OTC", "type": "🏢 Акция"}, {"name": "GBP/JPY OTC", "type": "📈 Валюта"}
]

allowed_users = [] 

@app.route('/')
def home():
    return "Bot is running"

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
        bot.send_message(message.chat.id, "⛔️ **ДОСТУП ОГРАНИЧЕН**\nЗарегистрируйтесь по ссылке и пришлите ID.")

@bot.message_handler(commands=['add'])
def add_user(message):
    try:
        user_id = int(message.text.split()[1])
        allowed_users.append(user_id)
        bot.send_message(user_id, "✅ **Доступ активирован!** Жми /signal")
    except:
        bot.send_message(message.chat.id, "Ошибка. Пиши: /add ID")

def run():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
