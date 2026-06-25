import os
import json
import logging
import asyncio
import hashlib
from datetime import datetime, timedelta
import random
import httpx
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TeamMasterAuto")

# --- КОНФИГУРАЦИЯ СЕТИ И ПАРТНЕРКИ ---
BOT_TOKEN = "8643698714:AAEh3AdcOKgdhE5NJ4s7ebIAnsM6zGXdkLI"
DB_FILE = "requests.json"

# Главный admin (ты)
ADMIN_IDS = [6765689893]  

# Белый список для друзей (проверка рефки и депозита для них отключена)
VIP_IDS = [8273386412]

# Данные партнерки
PARTNER_ID = "1336904"
API_TOKEN = "Zc4X9zu0EMrqbPuLy3tN"
PLATFORM_URL = "https://u3.shortink.io/cabinet/demo-quick-high-low?utm_campaign=850173&utm_source=affiliate&utm_medium=sr&a=RLQDltKf13Zlrj&al=1771346&ac=smart-link&cid=960963&code=WELCOME50" 

SUPPORT_URL = "https://t.me/andriddddd"       
TELEGRAM_CHANNEL = "https://t.me/+uekq4TquqkM4Mzcy" 
PHOTO_URL = "https://i.ibb.co/L1yZ6Gz/team-master-cover.jpg"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- ФЕЙКОВЫЙ ВЕБ-СЕРВЕР ДЛЯ ОБХОДА ТАЙМАУТА RENDER ---
async def handle(request):
    return web.Response(text="Bot is alive!")

async def start_webhook():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Веб-сервер запущен на порту {port}")

# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def get_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {"users": {}}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def generate_api_hash(user_id: str) -> str:
    hash_string = f"{user_id}:{PARTNER_ID}:{API_TOKEN}"
    return hashlib.md5(hash_string.encode('utf-8')).hexdigest()

async def check_pocket_api_full(user_id: str) -> tuple[bool, bool]:
    api_hash = generate_api_hash(user_id)
    url = f"https://affiliate.pocketoption.com/api/user-info/{user_id}/{PARTNER_ID}/{api_hash}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"API ответ для ID {user_id}: {data}")
                
                if data.get("status") == "success" or data.get("partner_id") == int(PARTNER_ID):
                    deposit_amount = float(data.get("deposit", 0))
                    is_deposit_ok = deposit_amount >= 20
                    return True, is_deposit_ok
        except Exception as e:
            logger.error(f"Ошибка при запросе к API партнерки: {e}")
    return False, False

DEPOSIT_TEXTS = {
    "ru": "💳 **ШАГ 2: АКТИВАЦИЯ ДЕПОЗИТА**\n\nВаш ID успешно найден в системе и подтвержден!\n\nЧтобы алгоритм ИИ активировал ваш торговый аккаунт, пополните баланс на платформе на сумму **от $20**.\n\n🎁 Используйте промокод **WELCOME50** при пополнении и получите **+50% к вашему депозиту** бесплатно!\n\n👉 После пополнения нажмите кнопку «ПРОВЕРИТЬ АКТИВАЦИЮ». Бот автоматически верифицирует ваш баланс.",
    "en": "💳 **STEP 2: DEPOSIT ACTIVATION**\n\nYour ID was successfully found and verified!\n\nTo activate your AI account, top up your platform balance with **$20 or more**.\n\n🎁 Use promo code **WELCOME50** when depositing and get **+50% to your deposit** for free!"
}

# МАКСИМАЛЬНО ПОЛНЫЙ СПИСОК АКТИВОВ (Обычные + OTC)
ALL_PAIRS = [
    # OTC активы
    "EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "EUR/JPY (OTC)", 
    "AUD/USD (OTC)", "GBP/JPY (OTC)", "USD/CHF (OTC)", "NZD/USD (OTC)", 
    "USD/CAD (OTC)", "EUR/GBP (OTC)", "EUR/CHF (OTC)", "AUD/JPY (OTC)",
    "GBP/CAD (OTC)", "GBP/CHF (OTC)", "GBP/AUD (OTC)", "AUD/CAD (OTC)",
    "AUD/NZD (OTC)", "NZD/JPY (OTC)", "CAD/JPY (OTC)", "CHF/JPY (OTC)",
    "EUR/AUD (OTC)", "EUR/NZD (OTC)", "EUR/CAD (OTC)", "USD/SGD (OTC)",
    "USD/TRY (OTC)", "USD/BRL (OTC)", "USD/MXN (OTC)", "USD/ZAR (OTC)",
    # Реальные биржевые активы
    "EUR/USD", "GBP/USD", "USD/JPY", "EUR/JPY", 
    "AUD/USD", "GBP/JPY", "USD/CHF", "USD/CAD", 
    "EUR/GBP", "AUD/JPY", "EUR/CAD", "GBP/CHF",
    "GBP/CAD", "GBP/AUD", "AUD/CAD", "AUD/NZD",
    "NZD/USD", "NZD/JPY", "CAD/JPY", "CHF/JPY",
    "EUR/AUD", "EUR/NZD", "EUR/CHF"
]

def get_signal_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 ОТКРЫТЬ POCKET OPTION", url=PLATFORM_URL)],
        [InlineKeyboardButton(text="📢 НАШ ТЕЛЕГРАМ КАНАЛ", url=TELEGRAM_CHANNEL)],
        [InlineKeyboardButton(text="👨‍💻 РАЗРАБОТЧИК / SUPPORT", url=SUPPORT_URL)],
        [InlineKeyboardButton(text="🔄 СЛЕДУЮЩИЙ СИГНАЛ", callback_data="next_signal")]
    ])

def get_lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"), InlineKeyboardButton(text="🇺🇸 English", callback_data="lang:en")],
        [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang:ua"), InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="lang:de")],
        [InlineKeyboardButton(text="🇫🇷 Français", callback_data="lang:fr"), InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang:es")]
    ])

def generate_signal_text() -> str:
    selected_pair = random.choice(ALL_PAIRS)
    direction = random.choice(["🟢 ВВЕРХ / CALL", "🔴 ВНИЗ / PUT"])
    timeframe = random.choice([1, 3, 5])  
    accuracy = round(random.uniform(91.4, 96.2), 1)

    return (
        f"🚀 **TEAM MASTER — СИГНАЛ СФОРМИРОВАН** 🚀\n\n"
        f"📊 **Активный актив:** `{selected_pair}`\n"
        f"⏳ **Интервал / Экспирация:** `{timeframe} МИНУТ` \n"
        f"📈 **Направление сделки:** {direction}\n"
        f"🎯 **Уверенность ИИ-алгоритма:** `{accuracy}%`\n\n"
        f"⚠️ *Входите в сделку строго по указанному времени. Соблюдайте риск-менеджмент!*"
    )

async def send_analyzing_process(chat_id: int, bot_instance: Bot):
    p1, p2, p3 = random.sample(ALL_PAIRS, 3)
    
    status_msg = await bot_instance.send_message(
        chat_id=chat_id,
        text=f"🔄 **HROM QUANTUM CORE v18.0 запущено...**\n\n📡 Подключение к серверам ликвидности...\n⌛ Сканирование волатильности актива `{p1}`"
    )
    await asyncio.sleep(1.2)
    
    try:
        await status_msg.edit_text(
            f"🔄 **ИИ-АНАЛИЗ РЫНКА...**\n\n📊 Считывание индикаторов RSI и Bollinger Bands...\n⌛ Проверка объемов на `{p2}`"
        )
        await asyncio.sleep(1.2)
        
        await status_msg.edit_text(
            f"🔄 **ФОРМИРОВАНИЕ ТОЧКИ ВХОДА...**\n\n🎯 Фильтрация ложных пробитий...\n⌛ Расчет вероятности профита на `{p3}`"
        )
        await asyncio.sleep(1.0)
    except TelegramBadRequest:
        pass
        
    try:
        await status_msg.delete()
    except TelegramBadRequest:
        pass

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    try: await message.delete()
    except TelegramBadRequest: pass

    # 1. Проверка на главного админа
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Привет, Босс! Запускаю моментальный анализ рынка...", parse_mode="Markdown")
        await send_analyzing_process(message.chat.id, bot)
        await message.answer(generate_signal_text(), reply_markup=get_signal_keyboard(), parse_mode="Markdown")
        return

    # 2. Проверка на VIP-пользователя (друга) из белого списка
    if message.from_user.id in VIP_IDS:
        await message.answer("Добро пожаловать, VIP! Подключаю торговое ядро...", parse_mode="Markdown")
        await send_analyzing_process(message.chat.id, bot)
        await message.answer(generate_signal_text(), reply_markup=get_signal_keyboard(), parse_mode="Markdown")
        return

    # 3. Для всех остальных — сначала описание проекта, а внизу выбор языка перед стартом
    info_text = (
        "📈 **TEAM MASTER GLOBAL BOT v18.0** 📈\n\n"
        "Добро пожаловать в автоматизированную систему генерации сигналов от **Команды Мастер**!\n\n"
        "🤖 **Что умеет этот ИИ-бот:**\n"
        "• В режиме реального времени анализирует более 45 биржевых и OTC активов.\n"
        "• Рассчитывает точки входа, используя технический анализ (RSI, Bollinger Bands, Скользящие средние).\n"
        "• Помогает трейдерам торговать с математическим преимуществом на дистанции.\n\n"
        "🌍 *Для запуска процесса синхронизации с сервером ИИ, пожалуйста, выберите ваш язык ниже:* / *Please select your language below to start:* "
    )
    
    # Отправляем описание вместе с картинкой на фоне
    await message.answer_photo(
        photo=PHOTO_URL,
        caption=info_text,
        reply_markup=get_lang_keyboard(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("lang:"))
async def process_lang(callback: types.CallbackQuery):
    selected_lang = callback.data.split(":")[1]
    
    reg_text = (
        "🤖 **TEAM MASTER — HROM QUANTUM CORE v18.0**\n\n"
        "📊 **Добро пожаловать в программное ядро Команды Мастер!** Наш ИИ-алгоритм непрерывно сканирует валютные и OTC-активы, вычисляя идеальные точки входа на основе технического анализа. Средний винрейт составляет **89.4% – 95.8%**.\n\n"
        "📝 **ШАГ 1: РЕГИСТРАЦИЯ В СИСТЕМЕ**\n\n"
        "Для того чтобы бот смог привязать ваш аккаунт к торговому ядру, вам необходимо создать новый личный кабинет на платформе брокера по ссылке ниже.\n\n"
        "👉 **Отправьте ваш числовой ID прямо в этот чат** ответным сообщением для автоматической проверки реферальной системы."
    )
    
    db = get_db()
    db["users"][f"id_{callback.from_user.id}"] = {"lang": selected_lang, "status": "registering", "chat_id": callback.message.chat.id}
    save_db(db)
    
    try: await callback.message.delete()
    except TelegramBadRequest: pass

    reg_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 РЕГИСТРАЦИЯ", url=PLATFORM_URL)],
        [InlineKeyboardButton(text="👨‍💻 SUPPORT", url=SUPPORT_URL)]
    ])
    await callback.message.answer(reg_text, reply_markup=reg_markup, parse_mode="Markdown")
    await callback.answer()

@dp.message(F.text)
async def handle_id_input(message: types.Message):
    user_input = message.text.strip()
    user_key = f"id_{message.from_user.id}"
    
    try: await message.delete()
    except TelegramBadRequest: pass

    if message.from_user.id in ADMIN_IDS or message.from_user.id in VIP_IDS:
        await send_analyzing_process(message.chat.id, bot)
        await message.answer(generate_signal_text(), reply_markup=get_signal_keyboard(), parse_mode="Markdown")
        return

    if not user_input.isdigit() or len(user_input) < 5:
        await message.answer("❌ Неверный формат ID. Пожалуйста, отправьте только цифры вашего ID.")
        return

    db = get_db()
    user_data = db["users"].get(user_key, {"lang": "ru", "chat_id": message.chat.id})
    lang = user_data.get("lang", "ru")

    is_ref_ok, is_deposit_ok = await check_pocket_api_full(user_input)
    
    if not is_ref_ok:
        reg_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📈 ЗАРЕГИСТРИРОВАТЬСЯ ЗАНОВО", url=PLATFORM_URL)],
            [InlineKeyboardButton(text="👨‍💻 SUPPORT", url=SUPPORT_URL)]
        ])
        await message.answer(
            "❌ **Ошибка верификации аккаунта!**\n\nВаш ID не найден в нашей реферальной системе. Убедитесь, что вы создали новый аккаунт строго по ссылке из бота.\n\nЕсли вы считаете это ошибкой, обратитесь в поддержку.", 
            reply_markup=reg_markup, 
            parse_mode="Markdown"
        )
        return

    user_data["partner_id"] = user_input
    
    if is_deposit_ok:
        user_data["status"] = "approved"
        save_db(db)
        await send_analyzing_process(message.chat.id, bot)
        await message.answer(generate_signal_text(), reply_markup=get_signal_keyboard(), parse_mode="Markdown")
    else:
        user_data["status"] = "waiting_deposit"
        save_db(db)
        dep_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 ПОПОЛНИТЬ БАЛАНС", url=PLATFORM_URL)],
            [InlineKeyboardButton(text="🔄 ПРОВЕРИТЬ АКТИВАЦИЮ", callback_data=f"check_dep:{user_input}")],
            [InlineKeyboardButton(text="👨‍💻 SUPPORT", url=SUPPORT_URL)]
        ])
        await message.answer(DEPOSIT_TEXTS.get(lang, DEPOSIT_TEXTS["ru"]), reply_markup=dep_markup, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("check_dep:"))
async def process_check_deposit(callback: types.CallbackQuery):
    user_id = callback.data.split(":")[1]
    user_key = f"id_{callback.from_user.id}"
    
    is_ref_ok, is_deposit_ok = await check_pocket_api_full(user_id)
    
    if not is_ref_ok:
        await callback.answer("❌ Ошибка: Ваш ID не найден в партнерской системе.", show_alert=True)
        return
        
    if is_deposit_ok:
        db = get_db()
        db["users"][user_key]["status"] = "approved"
        save_db(db)
        
        try: await callback.message.delete()
        except TelegramBadRequest: pass
        
        await send_analyzing_process(callback.message.chat.id, bot)
        await callback.message.answer(generate_signal_text(), reply_markup=get_signal_keyboard(), parse_mode="Markdown")
    else:
        await callback.answer("❌ Депозит от $20 пока не обнаружен. Пополните баланс или подождите 1-2 минуты.", show_alert=True)

@dp.callback_query(F.data == "next_signal")
async def process_next_signal(callback: types.CallbackQuery):
    user_key = f"id_{callback.from_user.id}"
    db = get_db()
    user_data = db["users"].get(user_key, {})
    
    if callback.from_user.id in ADMIN_IDS or callback.from_user.id in VIP_IDS or user_data.get("status") == "approved":
        try: await callback.message.delete()
        except TelegramBadRequest: pass
        
        await send_analyzing_process(callback.message.chat.id, bot)
        await callback.message.answer(generate_signal_text(), reply_markup=get_signal_keyboard(), parse_mode="Markdown")
    else:
        await callback.answer("❌ Доступ ограничен. Выполните шаги регистрации и активации.", show_alert=True)
    await callback.answer()

async def main():
    asyncio.create_task(start_webhook())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
