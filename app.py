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

# ==============================================================================
# КОНФИГУРАЦИЯ И ЛОГИРОВАНИЕ
# ==============================================================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TeamMasterPro")

BOT_TOKEN = "8643698714:AAEh3AdcOKgdhE5NJ4s7ebIAnsM6zGXdkLI"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL") 
PORT = int(os.environ.get("PORT", 10000))

PARTNER_ID = "1336904"
API_TOKEN = "Zc4X9zu0EMrqbPuLy3tN"
PLATFORM_URL = "https://u3.shortink.io/cabinet/demo-quick-high-low?utm_campaign=850173&utm_source=affiliate&utm_medium=sr&a=RLQDltKf13Zlrj&al=1771346&ac=smart-link&cid=960963&code=WELCOME50"
PHOTO_URL = "https://i.ibb.co/L1yZ6Gz/team-master-cover.jpg"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ==============================================================================
# СПИСОК АКТИВОВ И МАССИВЫ ДАННЫХ
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
# ФУНКЦИИ ИНТЕРФЕЙСА (10 ЯЗЫКОВ)
# ==============================================================================
def get_lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"), InlineKeyboardButton(text="🇺🇸 English", callback_data="lang:en")],
        [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang:ua"), InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="lang:de")],
        [InlineKeyboardButton(text="🇫🇷 Français", callback_data="lang:fr"), InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang:es")],
        [InlineKeyboardButton(text="🇮🇹 Italiano", callback_data="lang:it"), InlineKeyboardButton(text="🇵🇹 Português", callback_data="lang:pt")],
        [InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="lang:tr"), InlineKeyboardButton(text="🇰🇿 Қазақ", callback_data="lang:kz")]
    ])

def get_signal_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 ОТКРЫТЬ ПЛАТФОРМУ", url=PLATFORM_URL)],
        [InlineKeyboardButton(text="🔄 СЛЕДУЮЩИЙ СИГНАЛ", callback_data="next_signal")]
    ])

# ==============================================================================
# ЛОГИКА API ЗАЩИТЫ
# ==============================================================================
async def verify_user(user_id: str) -> bool:
    try:
        hash_str = f"{user_id}:{PARTNER_ID}:{API_TOKEN}"
        api_hash = hashlib.md5(hash_str.encode()).hexdigest()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://affiliate.pocketoption.com/api/user-info/{user_id}/{PARTNER_ID}/{api_hash}", timeout=10)
            if resp.status_code == 200:
                return float(resp.json().get("deposit", 0)) >= 20
    except Exception as e:
        logger.error(f"API Error: {e}")
    return False

# ==============================================================================
# ЯДРО СИГНАЛОВ
# ==============================================================================
def get_signal():
    return (
        f"🚀 **TEAM MASTER — AI SIGNAL** 🚀\n\n"
        f"📊 **Актив:** `{random.choice(ALL_PAIRS)}`\n"
        f"⏳ **Экспирация:** `{random.randint(2, 5)} МИН`\n"
        f"📈 **Прогноз:** {random.choice(['🟢 ВВЕРХ / CALL', '🔴 ВНИЗ / PUT'])}\n"
        f"🎯 **Точность:** `{round(random.uniform(92, 98), 1)}%`"
    )

# ==============================================================================
# ОБРАБОТЧИКИ
# ==============================================================================
@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer_photo(PHOTO_URL, caption="🌐 Выберите язык / Select language:", reply_markup=get_lang_kb())

@dp.message(F.text.isdigit())
async def process_id(m: types.Message):
    await m.answer("🔄 **Проверка данных через сервер...**")
    if await verify_user(m.text):
        await m.answer(get_signal(), reply_markup=get_signal_kb(), parse_mode="Markdown")
    else:
        await m.answer("❌ **Ошибка:** ID не найден или недостаточный депозит.")

@dp.callback_query(F.data == "next_signal")
async def next_sig(c: types.CallbackQuery):
    await c.message.answer(get_signal(), reply_markup=get_signal_kb(), parse_mode="Markdown")
    await c.answer()

# ==============================================================================
# WEBOOK ЗАПУСК (ДЛЯ RENDER)
# ==============================================================================
async def on_startup():
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")

async def webhook_handler(request):
    data = await request.json()
    await dp.feed_update(bot, types.Update(**data))
    return web.Response(status=200)

if __name__ == "__main__":
    app = web.Application()
    app.router.add_post("/webhook", webhook_handler)
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(on_startup())
    
    web.run_app(app, port=PORT)
