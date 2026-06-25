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

# --- ЛОГИРОВАНИЕ ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TeamMasterAuto")

# --- КОНФИГУРАЦИЯ ---
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

# --- ВСЕ АКТИВЫ (ПОЛНЫЙ СПИСОК) ---
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

# --- ФЕЙКОВЫЙ ВЕБ-СЕРВЕР ДЛЯ RENDER ---
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="Bot is alive!"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()

# --- БАЗА И API ---
def get_db():
    if not os.path.exists(DB_FILE): return {"users": {}}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {"users": {}}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def generate_api_hash(user_id: str) -> str:
    return hashlib.md5(f"{user_id}:{PARTNER_ID}:{API_TOKEN}".encode()).hexdigest()

async def check_pocket_api_full(user_id: str) -> tuple[bool, bool]:
    api_hash = generate_api_hash(user_id)
    url = f"https://affiliate.pocketoption.com/api/user-info/{user_id}/{PARTNER_ID}/{api_hash}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" or data.get("partner_id") == int(PARTNER_ID):
                    return True, float(data.get("deposit", 0)) >= 20
        except Exception as e: logger.error(f"API Error: {e}")
    return False, False

# --- ФУНКЦИИ КЛАВИАТУР ---
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

# --- ГЕНЕРАЦИЯ СИГНАЛОВ ---
def generate_signal_text() -> str:
    return (
        f"🚀 **TEAM MASTER — СИГНАЛ СФОРМИРОВАН** 🚀\n\n"
        f"📊 **Активный актив:** `{random.choice(ALL_PAIRS)}`\n"
        f"⏳ **Интервал / Экспирация:** `{random.randint(2, 5)} МИНУТ` \n"
        f"📈 **Направление сделки:** {random.choice(['🟢 ВВЕРХ / CALL', '🔴 ВНИЗ / PUT'])}\n"
        f"🎯 **Уверенность ИИ-алгоритма:** `{round(random.uniform(91.4, 96.2), 1)}%`\n\n"
        f"⚠️ *Соблюдайте риск-менеджмент!*"
    )

async def send_analyzing_process(chat_id: int, bot_instance: Bot):
    wait_time = random.uniform(5, 60) / 3
    status_msg = await bot_instance.send_message(chat_id, "🔄 **Анализ ликвидности...**")
    await asyncio.sleep(wait_time)
    await status_msg.edit_text("🔄 **ИИ-АНАЛИЗ РЫНКА...**")
    await asyncio.sleep(wait_time)
    await status_msg.edit_text("🔄 **ФОРМИРОВАНИЕ ТОЧКИ ВХОДА...**")
    await asyncio.sleep(wait_time)
    try: await status_msg.delete()
    except: pass

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id in ADMIN_IDS or message.from_user.id in VIP_IDS:
        await send_analyzing_process(message.chat.id, bot)
        await message.answer(generate_signal_text(), reply_markup=get_signal_keyboard())
    else:
        await message.answer_photo(PHOTO_URL, caption="Выберите язык:", reply_markup=get_lang_keyboard())

@dp.message(F.text)
async def handle_id_input(message: types.Message):
    if message.text.isdigit():
        is_ref, is_dep = await check_pocket_api_full(message.text)
        if is_ref and is_dep:
            await send_analyzing_process(message.chat.id, bot)
            await message.answer(generate_signal_text(), reply_markup=get_signal_keyboard())
        else:
            await message.answer("❌ ID не найден или нет депозита.")

@dp.callback_query(F.data == "next_signal")
async def next_s(c: types.CallbackQuery):
    await send_analyzing_process(c.message.chat.id, bot)
    await c.message.answer(generate_signal_text(), reply_markup=get_signal_keyboard())

# --- ЗАПУСК ---
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(start_web_server())
    loop.run_until_complete(bot.delete_webhook(drop_pending_updates=True))
    dp.run_polling(bot)
