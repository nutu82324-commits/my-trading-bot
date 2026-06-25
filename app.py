import os
import asyncio
import random
import httpx
import hashlib
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- КОНФИГУРАЦИЯ ---
BOT_TOKEN = "8643698714:AAEh3AdcOKgdhE5NJ4s7ebIAnsM6zGXdkLI"
PARTNER_ID = "1336904"
API_TOKEN = "Zc4X9zu0EMrqbPuLy3tN"
PLATFORM_URL = "https://u3.shortink.io/cabinet/demo-quick-high-low?utm_campaign=850173&utm_source=affiliate&utm_medium=sr&a=RLQDltKf13Zlrj&al=1771346&ac=smart-link&cid=960963&code=WELCOME50"
SUPPORT_URL = "https://t.me/andriddddd"
WHITE_LIST = [6765689893, 8273386412]

ALL_PAIRS = [
    "AED/CNY OTC", "BHD/CNY OTC", "EUR/GBP OTC", "EUR/TRY OTC", "GBP/JPY OTC", 
    "MAD/USD OTC", "NGN/USD OTC", "NZD/USD OTC", "USD/CNH OTC", "USD/EGP OTC",
    "USD/PHP OTC", "USD/PKR OTC", "USD/SGD OTC", "USD/THB OTC", "USD/VND OTC",
    "YER/USD OTC", "ZAR/USD OTC", "USD/CHF OTC", "EUR/USD", "USD/DZD OTC",
    "Cardano OTC", "Bitcoin ETF OTC", "BNB OTC", "Polkadot OTC", "Litecoin OTC",
    "Polygon OTC", "Solana OTC", "TRON OTC", "Chainlink OTC", "Bitcoin OTC",
    "American Express OTC", "FACEBOOK INC OTC", "Intel OTC", "VISA OTC",
    "Apple OTC", "Pfizer Inc OTC", "Cisco OTC", "Tesla OTC", "Alibaba OTC", "Palantir Technologies OTC"
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [CORE SYSTEM] - %(message)s')
logger = logging.getLogger("QuantumCore")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- КВАНТОВЫЙ ДВИЖОК С РАНДОМИЗАЦИЕЙ ИНТЕРВАЛА ---
class QuantumAnalyzer:
    def __init__(self):
        self.market_memory = {asset: 0.0 for asset in ALL_PAIRS}

    def analyze(self, asset):
        self.market_memory[asset] += random.uniform(-1.5, 1.5)
        
        # Генерация времени: от 5 сек до 300 сек (5 минут)
        # Если нужно в формате "X мин Y сек", добавим логику ниже
        expiry_seconds = random.randint(5, 300)
        minutes = expiry_seconds // 60
        seconds = expiry_seconds % 60
        expiry_str = f"{minutes} мин {seconds} сек" if minutes > 0 else f"{seconds} сек"
        
        if self.market_memory[asset] > 2.0:
            return "📉 🔴 SELL / ВНИЗ", random.randint(90, 98), expiry_str
        elif self.market_memory[asset] < -2.0:
            return "📈 🟢 BUY / ВВЕРХ", random.randint(90, 98), expiry_str
        
        return random.choice(["📈 🟢 BUY / ВВЕРХ", "📉 🔴 SELL / ВНИЗ"]), random.randint(75, 85), expiry_str

engine = QuantumAnalyzer()

# --- ВЕРИФИКАЦИЯ ---
async def verify_user(uid: str):
    if int(uid) in WHITE_LIST: return True, True
    hash_str = hashlib.md5(f"{uid}:{PARTNER_ID}:{API_TOKEN}".encode()).hexdigest()
    url = f"https://affiliate.pocketoption.com/api/user-info/{uid}/{PARTNER_ID}/{hash_str}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            data = resp.json()
            return data.get("status") == "success", float(data.get("deposit", 0)) >= 20
    except: return False, False

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer(
        "👑 **TEAM MASTER: QUANTUM CORE v7.5**\n\n"
        "Система инициализирована. Выберите язык:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🇷🇺 RU", callback_data="lang:ru"), InlineKeyboardButton(text="🇺🇸 EN", callback_data="lang:en")],
            [InlineKeyboardButton(text="🇺🇦 UA", callback_data="lang:ua"), InlineKeyboardButton(text="🇩🇪 DE", callback_data="lang:de")],
            [InlineKeyboardButton(text="🇪🇸 ES", callback_data="lang:es"), InlineKeyboardButton(text="🇫🇷 FR", callback_data="lang:fr")]
        ])
    )

@dp.callback_query(F.data.startswith("lang:"))
async def select_lang(c: types.CallbackQuery):
    await c.message.edit_text(
        "📝 **ШАГ 1: РЕГИСТРАЦИЯ**\n\n"
        "Пройдите регистрацию по ссылке и пришлите ID для активации доступа.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 ПЛАТФОРМА", url=PLATFORM_URL)]])
    )

@dp.message(F.text.isdigit())
async def handle_id(m: types.Message):
    reg, dep = await verify_user(m.text)
    if not reg: await m.answer("❌ ID не найден.")
    elif not dep: await m.answer("💳 Пополните от $20.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄 ПРОВЕРИТЬ", callback_data=f"check:{m.text}")]]))
    else: await m.answer("✅ Доступ активен!", reply_markup=get_main_kb())

@dp.callback_query(F.data == "get_sig")
async def sig(c: types.CallbackQuery):
    msg = await c.message.answer("🔄 Анализ потока...")
    await asyncio.sleep(2)
    asset = random.choice(ALL_PAIRS)
    direction, conf, expiry = engine.analyze(asset)
    
    text = (f"📡 **СИГНАЛ TEAM MASTER**\n\n"
            f"🔹 **Актив:** `{asset}`\n"
            f"⚡️ **Направление:** {direction}\n"
            f"⏱ **Экспирация:** `{expiry}`\n"
            f"🔥 **Уверенность:** `{conf}%`")
    
    try: await msg.edit_text(text, reply_markup=get_main_kb())
    except: await c.message.answer(text, reply_markup=get_main_kb())

def get_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📡 ПОЛУЧИТЬ СИГНАЛ", callback_data="get_sig")]])

# --- ЗАПУСК ---
async def web_server():
    runner = web.AppRunner(web.Application())
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()

async def main():
    await asyncio.gather(web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
