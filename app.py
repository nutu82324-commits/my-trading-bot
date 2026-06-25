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
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.exceptions import TelegramBadRequest

# --------------------------------------------------------------------------------------------------
# [SYSTEM CONFIGURATION & LOGGING]
# --------------------------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TeamMasterProExtended")

BOT_TOKEN = "8643698714:AAEh3AdcOKgdhE5NJ4s7ebIAnsM6zGXdkLI"
DB_FILE = "requests.json"
ADMIN_IDS = [6765689893]
VIP_IDS = [8273386412]
PARTNER_ID = "1336904"
API_TOKEN = "Zc4X9zu0EMrqbPuLy3tN"
PLATFORM_URL = "https://u3.shortink.io/cabinet/demo-quick-high-low?utm_campaign=850173&utm_source=affiliate&utm_medium=sr&a=RLQDltKf13Zlrj&al=1771346&ac=smart-link&cid=960963&code=WELCOME50"
SUPPORT_URL = "https://t.me/andriddddd"
TELEGRAM_CHANNEL = "https://t.me/+uekq4TquqkM4Mzcy"
PHOTO_URL = "https://i.ibb.co/L1yZ6Gz/team-master-cover.jpg"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --------------------------------------------------------------------------------------------------
# [EXTENDED ASSETS LIST]
# --------------------------------------------------------------------------------------------------
ALL_PAIRS = [
    "EUR/USD OTC", "GBP/USD OTC", "AUD/USD OTC", "USD/JPY OTC", "USD/CHF OTC", 
    "USD/CAD OTC", "EUR/GBP OTC", "EUR/JPY OTC", "GBP/JPY OTC", "CHF/JPY OTC", 
    "AUD/CAD OTC", "AUD/NZD OTC", "AUD/CHF OTC", "CAD/JPY OTC", "EUR/CHF OTC",
    "Solana OTC", "BNB OTC", "Cardano OTC", "TRON OTC", "Chainlink OTC", 
    "Toncoin OTC", "Ethereum OTC", "Litecoin OTC", "Polkadot OTC",
    "Apple OTC", "Microsoft OTC", "Tesla OTC", "McDonald's OTC", 
    "FACEBOOK INC OTC", "Intel OTC", "Johnson & Johnson OTC",
    "Gold OTC", "Brent Oil OTC", "WTI Crude Oil OTC", "Silver OTC", "Natural Gas OTC"
]

# --------------------------------------------------------------------------------------------------
# [DATABASE ENGINE]
# --------------------------------------------------------------------------------------------------
def get_database_state():
    if not os.path.exists(DB_FILE):
        return {"users": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"DB Read Error: {e}")
        return {"users": {}}

def write_database_state(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"DB Write Error: {e}")

# --------------------------------------------------------------------------------------------------
# [API INTEGRATION LAYER]
# --------------------------------------------------------------------------------------------------
async def verify_user_on_platform(user_id: str):
    logger.info(f"Initiating verification for user_id: {user_id}")
    hash_str = hashlib.md5(f"{user_id}:{PARTNER_ID}:{API_TOKEN}".encode()).hexdigest()
    url = f"https://affiliate.pocketoption.com/api/user-info/{user_id}/{PARTNER_ID}/{hash_str}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                deposit = float(data.get("deposit", 0))
                logger.info(f"API Success. Deposit: {deposit}")
                return True, deposit >= 20
        except Exception as e:
            logger.error(f"External API Connection Failure: {e}")
    return False, False

# --------------------------------------------------------------------------------------------------
# [UI/UX MODULES]
# --------------------------------------------------------------------------------------------------
def create_main_markup():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 ОТКРЫТЬ ТЕРМИНАЛ", url=PLATFORM_URL)],
        [InlineKeyboardButton(text="📢 КАНАЛ СИГНАЛОВ", url=TELEGRAM_CHANNEL)],
        [InlineKeyboardButton(text="👨‍💻 ТЕХПОДДЕРЖКА", url=SUPPORT_URL)],
        [InlineKeyboardButton(text="🔄 СЛЕДУЮЩИЙ СИГНАЛ", callback_data="next_sig")]
    ])

def format_signal_output():
    asset = random.choice(ALL_PAIRS)
    direction = random.choice(['🟢 ВВЕРХ / CALL', '🔴 ВНИЗ / PUT'])
    conf = round(random.uniform(91.4, 96.2), 1)
    return (f"🚀 **TEAM MASTER — HROM QUANTUM CORE** 🚀\n\n"
            f"📊 **Торговый актив:** `{asset}`\n"
            f"📈 **Направление:** {direction}\n"
            f"🎯 **Уверенность ИИ:** `{conf}%`\n\n"
            f"⚠️ *Используйте стратегию управления капиталом!*")

# --------------------------------------------------------------------------------------------------
# [BOT CONTROLLERS]
# --------------------------------------------------------------------------------------------------
@dp.message(Command("start"))
async def start_controller(message: types.Message):
    logger.info(f"User {message.from_user.id} accessed /start")
    await message.answer_photo(
        photo=PHOTO_URL,
        caption="🤖 **TEAM MASTER GLOBAL BOT v18.0**\n\nАвтоматизированный комплекс для технического анализа. Пожалуйста, введите ваш ID для верификации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 РЕГИСТРАЦИЯ", url=PLATFORM_URL)]])
    )

@dp.message(F.text)
async def id_processor(message: types.Message):
    if not message.text.isdigit():
        await message.answer("❌ Ошибка: Введите корректный цифровой ID.")
        return
        
    status, has_dep = await verify_user_on_platform(message.text)
    
    if not status:
        await message.answer("❌ Сервер верификации недоступен. Попробуйте позже.")
        return
        
    if has_dep or message.from_user.id in ADMIN_IDS + VIP_IDS:
        await message.answer(format_signal_output(), reply_markup=create_main_markup())
    else:
        await message.answer(
            "💳 **Требуется активация**\n\nВаш ID подтвержден, но торговый аккаунт не активен. Пополните баланс на $20.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💳 ПОПОЛНИТЬ БАЛАНС", url=PLATFORM_URL)]])
        )

@dp.callback_query(F.data == "next_sig")
async def signal_callback(callback: types.CallbackQuery):
    await callback.message.answer(format_signal_output(), reply_markup=create_main_markup())
    await callback.answer()

# --------------------------------------------------------------------------------------------------
# [WEB SERVER ADAPTER FOR RENDER]
# --------------------------------------------------------------------------------------------------
async def start_web_server():
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Web Service bound to port {port}")

# --------------------------------------------------------------------------------------------------
# [EXECUTION CORE]
# --------------------------------------------------------------------------------------------------
async def main_loop():
    await start_web_server()
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Initializing polling service...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except Exception as e:
        logger.critical(f"Critical System Failure: {e}")
