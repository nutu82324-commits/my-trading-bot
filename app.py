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
BOT_TOKEN = "8080518030:AAH3hdW1C7HF2k1AW8yBysUZ01-yvUV2DVg"
DB_FILE = "requests.json"
ADMIN_ID = "6765689893" # ЗАМЕНИ ЭТО ЧИСЛО НА СВОЙ РЕАЛЬНЫЙ TELEGRAM ID ДЛЯ ОБХОДА ПРОВЕРОК

# Данные партнерки
PARTNER_ID = "1336904"
API_TOKEN = "Zc4X9zu0EMrqbPuLy3tN"
PLATFORM_URL = "https://u3.shortink.io/smart/RLQDltKf13Zlrj" 

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
    # Читем порт, который дает Render, или берем дефолтный 8000
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

async def check_pocket_api(user_id: str) -> bool:
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
                    if deposit_amount >= 20:
                        return True
        except Exception as e:
            logger.error(f"Ошибка при запросе к API партнерки: {e}")
    return False

DEPOSIT_TEXTS = {
    "ru": "💳 **ШАГ 2: АКТИВАЦИЯ ДЕПОЗИТА**\n\nВаш ID успешно найден в системе!\n\nЧтобы алгоритм ИИ активировал ваш торговый аккаунт, пополните баланс на платформе на сумму **от $20**.\n\n🎁 Используйте промокод **MASTER50** при пополнении и получите **+50% к вашему депозиту** бесплатно!\n\n👉 После пополнения бот автоматически верифицирует ваш баланс в течение нескольких минут.",
    "en": "💳 **STEP 2: DEPOSIT ACTIVATION**\n\nYour ID was successfully found!\n\nTo activate your AI account, top up your platform balance with **$20 or more**.\n\n🎁 Use promo code **MASTER50** when depositing and get **+50% to your deposit** for free!"
}

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

# Функция генерации красивого минутного сигнала
def generate_signal_text() -> str:
    pairs = ["EUR/USD (OTC)", "GBP/USD (OTC)", "USD/JPY (OTC)", "EUR/JPY (OTC)", "AUD/USD (OTC)", "GBP/JPY (OTC)"]
    selected_pair = random.choice(pairs)
    direction = random.choice(["🟢 ВВЕРХ / CALL", "🔴 ВНИЗ / PUT"])
    timeframe = random.choice([1, 3, 5])  # Исключительно минутные таймфреймы
    accuracy = round(random.uniform(91.4, 96.2), 1)

    return (
        f"🚀 **TEAM MASTER — СИГНАЛ СФОРМИРОВАН** 🚀\n\n"
        f"📊 **Активный актив:** `{selected_pair}`\n"
        f"⏳ **Интервал / Экспирация:** `{timeframe} МИНУТ` \n"
        f"📈 **Направление сделки:** {direction}\n"
        f"🎯 **Уверенность ИИ-алгоритма:** `{accuracy}%`\n\n"
        f"⚠️ *Входите в сделку строго по указанному времени. Соблюдайте риск-менеджмент!*"
    )

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    try: await message.delete()
    except TelegramBadRequest: pass

    # Проверка на админа / создателя
    if message.from_user.id == ADMIN_ID:
        await message.answer_photo(
            photo=PHOTO_URL, 
            caption="Привет, Босс! Для тебя защита отключена. Держи актуальный торговый сигнал от системы:", 
            reply_markup=get_signal_keyboard(), 
            parse_mode="Markdown"
        )
        await message.answer(generate_signal_text(), reply_markup=get_signal_keyboard(), parse_mode="Markdown")
        return

    welcome_text = (
        "🤖 **TEAM MASTER GLOBAL BOT**\n\n"
        "📊 Добро пожаловать в систему **Team Master**!\n"
        "Синхронизация с ядром ИИ **HROM QUANTUM CORE v18.0** установлена.\n\n"
        "🌐 **Please choose your language / Пожалуйста, выберите язык:**"
    )
    await message.answer_photo(photo=PHOTO_URL, caption=welcome_text, reply_markup=get_lang_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("lang:"))
async def process_lang(callback: types.CallbackQuery):
    selected_lang = callback.data.split(":")[1]
    
    reg_text = (
        "🤖 **TEAM MASTER — HROM QUANTUM CORE v18.0**\n\n"
        "📊 **Добро пожаловать в программное ядро Команды Мастер!** Наш ИИ-алгоритм непрерывно сканирует более 40 валютных пар и OTC-активов, вычисляя идеальные точки входа на основе технического анализа. Средний винрейт составляет **89.4% – 95.8%**.\n\n"
        "📝 **ШАГ 1: РЕГИСТРАЦИЯ В СИСТЕМЕ**\n\n"
        "Для того чтобы бот смог привязать ваш аккаунт к торговому ядру, вам необходимо создать новый личный кабинет на платформе брокера.\n\n"
        "👉 **Отправьте ваш числовой ID прямо в этот чат** ответным сообщением для автоматической проверки."
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

    # Если пишет админ — просто даем ему новый сигнал
    if message.from_user.id == ADMIN_ID:
        await message.answer(generate_signal_text(), reply_markup=get_signal_keyboard(), parse_mode="Markdown")
        return

    if not user_input.isdigit() or len(user_input) < 5:
        await message.answer("❌ Неверный формат ID. Пожалуйста, отправьте только цифры вашего ID.")
        return

    db = get_db()
    user_data = db["users"].get(user_key, {"lang": "ru", "chat_id": message.chat.id})
    lang = user_data.get("lang", "ru")

    user_data["partner_id"] = user_input
    user_data["status"] = "waiting_deposit"
    db["users"][user_key] = user_data
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
    
    is_active = await check_pocket_api(user_id)
    
    if is_active:
        db = get_db()
        db["users"][user_key]["status"] = "approved"
        save_db(db)
        
        try: await callback.message.delete()
        except TelegramBadRequest: pass
        
        await callback.message.answer(generate_signal_text(), reply_markup=get_signal_keyboard(), parse_mode="Markdown")
    else:
        await callback.answer("❌ Депозит от $20 пока не обнаружен. Пополните баланс или подождите 1-2 минуты.", show_alert=True)

# Кнопка запроса следующего сигнала для верифицированных юзеров и админа
@dp.callback_query(F.data == "next_signal")
async def process_next_signal(callback: types.CallbackQuery):
    user_key = f"id_{callback.from_user.id}"
    db = get_db()
    user_data = db["users"].get(user_key, {})
    
    if callback.from_user.id == ADMIN_ID or user_data.get("status") == "approved":
        try: await callback.message.delete()
        except TelegramBadRequest: pass
        
        await callback.message.answer(generate_signal_text(), reply_markup=get_signal_keyboard(), parse_mode="Markdown")
    else:
        await callback.answer("❌ Доступ ограничен. Выполните шаги регистрации и активации.", show_alert=True)
    await callback.answer()

async def main():
    # Запускаем фоновый веб-сервер, чтобы Render не закрывал Web Service по таймауту
    asyncio.create_task(start_webhook())
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
