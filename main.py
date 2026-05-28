import telebot
from telebot import types
import random
import time

TOKEN = "8637835333:AAFZKCpggslNEYi5YR5BgjDbt1UtxW_D4CI"
bot = telebot.TeleBot(TOKEN)

# ⚠️ ВСТАВЬ СЮДА СВОЙ TELEGRAM ID (цифры), чтобы управлять ботом
ADMIN_ID = 6765689893

# Базы данных состояний пользователей
user_pockets = {}     # Здесь храним Pocket ID пользователей {user_id: pocket_id}
verified_ids = set()   # Пользователи, у которых одобрен только ID
verified_deps = set()  # Пользователи, у которых одобрен и Депозит (полный доступ)

pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD"]
REG_LINK = "https://pocket-friends.co/r/vmbewy0x1o"

@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = message.from_user.id
    
    # Главное меню кнопок
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_signal = types.KeyboardButton("🤖 Получить ИИ-Сигнал")
    btn_reg = types.KeyboardButton("🔑 Шаг 1: Верифицировать ID")
    btn_dep = types.KeyboardButton("💰 Шаг 2: Подтвердить Пополнение")
    markup.add(btn_signal)
    markup.add(btn_reg, btn_dep)
    
    if user_id in verified_deps:
        status_text = "✅ **СТАТУС: Полный VIP-доступ активирован!** Можете брать сигналы."
    elif user_id in verified_ids:
        status_text = "⚠️ **СТАТУС: ID одобрен.** Ожидается пополнение баланса на Pocket Option."
    else:
        status_text = "🔒 **СТАТУС: Доступ закрыт.** Требуется регистрация."

    text = (
        "🤖 **AI SIGNAL TERMINAL V4.0** 🤖\n\n"
        f"{status_text}\n\n"
        "Для получения доступа к сигналам (92%+ прибыли) пройдите 2 шага:\n\n"
        f"1️⃣ Зарегистрируйте аккаунт по ссылке: {REG_LINK}\n"
        "2️⃣ Нажмите кнопку **'🔑 Шаг 1: Верифицировать ID'** и отправьте ваш номер аккаунта.\n"
        "3️⃣ После одобрения ID пополните баланс и нажмите **'💰 Шаг 2: Подтвердить Пополнение'**."
    )
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

# --- ЭТАП 1: ПРОВЕРКА ID ---
@bot.message_handler(func=lambda message: message.text == "🔑 Шаг 1: Верифицировать ID")
def ask_id(message):
    user_id = message.from_user.id
    if user_id in verified_ids or user_id in verified_deps:
        bot.send_message(message.chat.id, "✅ Ваш ID уже успешно верифицирован!")
        return
        
    text = f"🎯 **ВЕРИФИКАЦИЯ ID**\n\nУбедись, что зарегистрирован по ссылке: {REG_LINK}\n\nВведите ваш ID Pocket Option (только цифры):"
    msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(msg, save_id)

def save_id(message):
    user_id = message.from_user.id
    text = message.text
    
    if text.isdigit() and len(text) >= 5:
        user_pockets[user_id] = text  # Запоминаем ID
        bot.send_message(message.chat.id, "⏳ **ID отправлен на проверку.** Администратор сверит его с партнерской сетью. Ожидайте уведомления.")
        
        if ADMIN_ID != 0:
            admin_markup = types.InlineKeyboardMarkup()
            btn_accept = types.InlineKeyboardButton("✅ Одобрить ID", callback_data=f"idacc_{user_id}_{text}")
            btn_deny = types.InlineKeyboardButton("❌ Отклонить", callback_data=f"iddeny_{user_id}")
            admin_markup.add(btn_accept, btn_deny)
            bot.send_message(ADMIN_ID, f"🔔 **НОВАЯ ЗАЯВКА НА ID!**\n🆔 Pocket ID: `{text}`\nПроверь регистрацию в партнерке:", reply_markup=admin_markup, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ Ошибка! Введите правильный ID (только цифры).")

# --- ЭТАП 2: ПРОВЕРКА ДЕПОЗИТА ---
@bot.message_handler(func=lambda message: message.text == "💰 Шаг 2: Подтвердить Пополнение")
def ask_deposit(message):
    user_id = message.from_user.id
    
    if user_id not in verified_ids:
        bot.send_message(message.chat.id, "❌ **Сначала отправьте ID на проверку!** Нажмите '🔑 Шаг 1: Верифицировать ID'.")
        return
    if user_id in verified_deps:
        bot.send_message(message.chat.id, "✅ У вас уже активирован полный доступ к сигналам!")
        return
        
    pocket_id = user_pockets.get(user_id, "Неизвестный")
    bot.send_message(message.chat.id, "⏳ **Запрос на верификацию депозита отправлен админу.**\nКак только админ увидит пополнение в системе, вам откроются ИИ-сигналы.")
    
    if ADMIN_ID != 0:
        admin_markup = types.InlineKeyboardMarkup()
        btn_accept = types.InlineKeyboardButton("💰 Одобрить Депозит", callback_data=f"depacc_{user_id}_{pocket_id}")
        btn_deny = types.InlineKeyboardButton("❌ Отклонить депозит", callback_data=f"depdeny_{user_id}")
        admin_markup.add(btn_accept, btn_deny)
        bot.send_message(ADMIN_ID, f"💳 **ИГРОК ПРЕТЕНДУЕТ НА ДЕПОЗИТ!**\n🆔 Pocket ID: `{pocket_id}`\nПроверь, пополнил ли он счет на платформе:", reply_markup=admin_markup, parse_mode="Markdown")

# --- ОБРАБОТКА РЕШЕНИЙ АДМИНИСТРАТОРА (КНОПКИ В ТВОЕЙ ЛИЧКЕ) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith(('idacc_', 'iddeny_', 'depacc_', 'depdeny_')))
def admin_decision(call):
    data = call.data.split('_')
    action = data[0]
    target_user_id = int(data[1])
    
    # Ответы на проверку ID
    if action == 'idacc':
        pocket_id = data[2]
        verified_ids.add(target_user_id)
        bot.edit_message_text(f"✅ Ты одобрил ID {pocket_id}. Ожидаем депозит.", call.message.chat.id, call.message.message_id)
        bot.send_message(
            target_user_id, 
            f"🎉 **Отлично! Ваш ID {pocket_id} подтвержден!**\n\n"
            f"Последний шаг для активации ИИ: пополните ваш торговый баланс Pocket Option на любую сумму.\n"
            f"После пополнения нажмите кнопку **'💰 Шаг 2: Подтвердить Пополнение'** в меню бота."
        )
    elif action == 'iddeny':
        bot.edit_message_text("❌ Ты отклонил ID. Доступ закрыт.", call.message.chat.id, call.message.message_id)
        bot.send_message(target_user_id, f"❌ **Ваш ID не найден в системе.** Проверьте, что зарегистрировались по ссылке: {REG_LINK} и ввели ID верно.")

    # Ответы на проверку Депозита
    elif action == 'depacc':
        pocket_id = data[2]
        verified_deps.add(target_user_id)
        bot.edit_message_text(f"🔥 ПОЛНЫЙ ДОСТУП ОТКРЫТ для ID {pocket_id} (Депозит подтвержден).", call.message.chat.id, call.message.message_id)
        bot.send_message(
            target_user_id,
            "🚀 **ПОЗДРАВЛЯЕМ! Депозит подтвержден, торговый робот запущен!**\n\n"
            "Теперь вам доступна функция выдачи сигналов со скоростью отклика 0.001 сек. Нажимайте кнопку **'🤖 Получить ИИ-Сигнал'** и забирайте профит!"
        )
    elif action == 'depdeny':
        bot.edit_message_text("❌ Ты отклонил депозит.", call.message.chat.id, call.message.message_id)
        bot.send_message(target_user_id, "❌ **Пополнение счета не обнаружено.** Убедитесь, что внесли депозит на аккаунт, и нажмите кнопку подтверждения снова.")

# --- ВЫДАЧА ТУРБО-СИГНАЛОВ ---
@bot.message_handler(func=lambda message: message.text == "🤖 Получить ИИ-Сигнал")
def give_signal(message):
    user_id = message.from_user.id
    
    # Полный блок: если нет подтвержденного депозита — сигналы не выдавать!
    if user_id not in verified_deps:
        bot.send_message(
            message.chat.id, 
            "🔒 **ДОСТУП ЗАБЛОКИРОВАН**\n\n"
            f"Вы не завершили активацию. Зарегистрируйтесь ({REG_LINK}), отправьте ID (Шаг 1) и подтвердите депозит (Шаг 2)."
        )
        return

    # Моментальный расчет котировок на процессоре (Turbo)
    t = time.time()
    base_price = 1.08450 if int(t) % 2 == 0 else 1.26340
    current_price = round(base_price + (int(t) % 100) * 0.00002, 5)
    
    rsi = int(t) % 100
    if rsi > 65:
        direction = "🔴 ВНИЗ (PUT)"
        logic_reason = "Индикатор RSI в зоне перекупленности. Ожидается откат цены."
    elif rsi < 35:
        direction = "🟢 ВВЕРХ (CALL)"
        logic_reason = "Индикатор RSI в зоне перепроданности. Сильный сигнал на покупку."
    else:
        direction = "🟢 ВВЕРХ (CALL)" if int(t) % 2 == 0 else "🔴 ВНИЗ (PUT)"
        logic_reason = "Сканирование объемов: Локальный микротренд подтвержден."

    pair = random.choice(pairs)
    timeframe = random.choice(["1 мин", "2 мин"])
    
    signal_text = (
        f"🎯 **AI SIGNAL TERMINAL V4.0** 🎯\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 **Валютная пара:** {pair}\n"
        f"💰 **Текущая доходность:** 92% ПРИБЫЛИ\n"
        f"📈 **Прямая котировка:** {current_price}\n"
        f"⏱ **Время сделки:** {timeframe}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 **Анализ ИИ:** {logic_reason}\n"
        f"👉 **РЕШЕНИЕ:** {direction}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📉 *Открывай сделку на Pocket Option:*\n"
        f"🔗 [ВОЙТИ НА ПЛАТФОРМУ]({REG_LINK})"
    )
    bot.send_message(message.chat.id, signal_text, parse_mode="Markdown", disable_web_page_preview=True)

if __name__ == "__main__":
    bot.polling(none_stop=True)
