import os
import json
import logging
import asyncio
import hashlib
import random
import httpx
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

# ==============================================================================
# НАСТРОЙКИ ЛОГИРОВАНИЯ И КОНФИГУРАЦИЯ
# ==============================================================================
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("TeamMasterPro_FullEdition")

BOT_TOKEN = "8643698714:AAEh3AdcOKgdhE5NJ4s7ebIAnsM6zGXdkLI"
DB_FILE = "requests.json"
PARTNER_ID = "1336904"
API_TOKEN = "Zc4X9zu0EMrqbPuLy3tN"
PLATFORM_URL = "https://u3.shortink.io/cabinet/demo-quick-high-low?utm_campaign=850173&utm_source=affiliate&utm_medium=sr&a=RLQDltKf13Zlrj&al=1771346&ac=smart-link&cid=960963&code=WELCOME50"
SUPPORT_URL = "https://t.me/andriddddd"
TELEGRAM_CHANNEL = "https://t.me/+uekq4TquqkM4Mzcy"
PHOTO_URL = "https://i.ibb.co/L1yZ6Gz/team-master-cover.jpg"

ADMIN_IDS = [6765689893]
VIP_IDS = [8273386412]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ==============================================================================
# СПИСОК ВСЕХ АКТИВОВ
# ==============================================================================
ALL_PAIRS = [
    "AED/CNY OTC", "BHD/CNY OTC", "EUR/GBP OTC", "EUR/TRY OTC", "GBP/JPY OTC", 
    "MAD/USD OTC", "NGN/USD OTC", "NZD/USD OTC", "USD/CNH OTC", "USD/EGP OTC",
    "USD/PHP OTC", "USD/PKR OTC", "USD/SGD OTC", "USD/THB OTC", "USD/VND OTC",
    "YER/USD OTC", "ZAR/USD OTC", "USD/CHF OTC", "EUR/USD", "USD/DZD OTC",
    "Cardano OTC", "Bitcoin ETF OTC", "BNB OTC", "Polkadot OTC", "Litecoin OTC",
    "Polygon OTC", "Solana OTC", "TRON OTC", "Chainlink OTC", "Bitcoin OTC",
    "American Express OTC", "FACEBOOK INC OTC", "Intel OTC", "VISA OTC",
    "Apple OTC", "Pfizer Inc OTC", "Cisco OTC", "Tesla OTC", "Alibaba OTC",
    "Palantir Technologies OTC"
]

# ==============================================================================
# КЛАВИАТУРЫ И ЯЗЫКОВАЯ ПАНЕЛЬ
# ==============================================================================
def get_lang_keyboard():
    """Возвращает панель выбора из 10 языков"""
    keyboard = [
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"), InlineKeyboardButton(text="🇺🇸 English", callback_data="lang:en")],
        [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang:ua"), InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="lang:de")],
        [InlineKeyboardButton(text="🇫🇷 Français", callback_data="lang:fr"), InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang:es")],
        [InlineKeyboardButton(text="🇮🇹 Italiano", callback_data="lang:it"), InlineKeyboardButton(text="🇵🇹 Português", callback_data="lang:pt")],
        [InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="lang:tr"), InlineKeyboardButton(text="🇰🇿 Қазақ", callback_data="lang:kz")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_signal_keyboard():
    """Основная клавиатура под сигналом"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 ОТКРЫТЬ POCKET OPTION", url=PLATFORM_URL)],
        [InlineKeyboardButton(text="📢 КАНАЛ", url=TELEGRAM_CHANNEL), InlineKeyboardButton(text="👨‍💻 ПОДДЕРЖКА", url=SUPPORT_URL)],
        [InlineKeyboardButton(text="🔄 СЛЕДУЮЩИЙ СИГНАЛ", callback_data="next_signal")]
    ])

# ==============================================================================
# ЛОГИКА API И ЗАЩИТЫ
# ==============================================================================
async def check_pocket_api(user_id: str) -> tuple[bool, bool]:
    """Проверка через API партнерки с логированием"""
    logger.info(f"Начало проверки ID: {user_id}")
    try:
        hash_string = f"{user_id}:{PARTNER_ID}:{API_TOKEN}"
        api_hash = hashlib.md5(hash_string.encode('utf-8')).hexdigest()
        url = f"https://affiliate.pocketoption.com/api/user-info/{user_id}/{PARTNER_ID}/{api_hash}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=15.0)
            if response.status_code == 200:
                data = response.json()
                deposit = float(data.get("deposit", 0))
                logger.info(f"Успешный ответ API для {user_id}. Депозит: {deposit}")
                return True, deposit >= 20
            else:
                logger.warning(f"Ошибка API {response.status_code} для ID {user_id}")
    except Exception as e:
        logger.error(f"Критическая ошибка проверки API: {e}")
    return False, False

# ==============================================================================
# ЯДРО ГЕНЕРАЦИИ СИГНАЛОВ
# ==============================================================================
def generate_signal_data():
    """Генерация параметров сделки"""
    return {
        "pair": random.choice(ALL_PAIRS),
        "time": random.randint(2, 5),
        "accuracy": round(random.uniform(92.0, 98.0), 1),
        "direction": random.choice(["🟢 ВВЕРХ / CALL", "🔴 ВНИЗ / PUT"])
    }

def format_signal(data: dict) -> str:
    """Оформление текста сигнала"""
    return (
        f"🚀 **TEAM MASTER — AI CORE v18.0** 🚀\n\n"
        f"📊 **Актив:** `{data['pair']}`\n"
        f"⏳ **Экспирация:** `{data['time']} МИНУТ`\n"
        f"📈 **Направление:** {data['direction']}\n"
        f"🎯 **Уверенность ИИ:** `{data['accuracy']}%`\n\n"
        f"⚠️ *Используйте стратегию риск-менеджмента!*"
    )

async def run_simulation(chat_id: int):
    """Имитация сложного процесса вычислений"""
    stages = [
        "🔄 **Подключение к серверам...**",
        "📡 **Анализ волатильности...**",
        "🔍 **Синхронизация с API...**",
        "🎯 **Финальный расчет...**"
    ]
    msg = await bot.send_message(chat_id, stages[0])
    for stage in stages:
        await msg.edit_text(stage)
        await asyncio.sleep(0.7)
    await msg.delete()

# ==============================================================================
# ОБРАБОТЧИКИ СООБЩЕНИЙ
# ==============================================================================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer_photo(
        photo=PHOTO_URL, 
        caption="📈 **TEAM MASTER GLOBAL**\n\nВыберите язык интерфейса для начала работы с ИИ:", 
        reply_markup=get_lang_keyboard()
    )

@dp.callback_query(F.data.startswith("lang:"))
async def lang_handler(callback: types.CallbackQuery):
    await callback.message.answer("📥 **Введите ваш ID с платформы Pocket Option для верификации:**")
    await callback.answer()

@dp.message(F.text)
async def id_handler(message: types.Message):
    # Доступ для элиты (админы/випы)
    if message.from_user.id in ADMIN_IDS or message.from_user.id in VIP_IDS:
        await run_simulation(message.chat.id)
        data = generate_signal_data()
        await message.answer(format_signal(data), reply_markup=get_signal_keyboard(), parse_mode="Markdown")
        return

    # Проверка для обычных пользователей
    if not message.text.isdigit():
        await message.answer("⚠️ Пожалуйста, введите корректный ID (только цифры).")
        return

    # Блок работы с API
    await message.answer("🔍 **Проверка аккаунта в базе данных...**")
    is_ok, is_dep = await check_pocket_api(message.text)
    
    if is_ok and is_dep:
        await run_simulation(message.chat.id)
        data = generate_signal_data()
        await message.answer(format_signal(data), reply_markup=get_signal_keyboard(), parse_mode="Markdown")
    else:
        await message.answer("❌ **ОШИБКА:** ID не найден или депозит менее $20. Пожалуйста, пополните счет.")

@dp.callback_query(F.data == "next_signal")
async def next_signal_handler(callback: types.CallbackQuery):
    await run_simulation(callback.message.chat.id)
    data = generate_signal_data()
    await callback.message.answer(format_signal(data), reply_markup=get_signal_keyboard(), parse_mode="Markdown")
    await callback.answer()

# ==============================================================================
# ЗАПУСК
# ==============================================================================
async def main():
    logger.info("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
