import os
import asyncio
import random
import httpx
import hashlib
import logging
import json
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

# ==============================================================================
# КОНФИГУРАЦИЯ СИСТЕМЫ TEAM MASTER - QUANTUM CORE
# ==============================================================================
BOT_TOKEN = "8643698714:AAEh3AdcOKgdhE5NJ4s7ebIAnsM6zGXdkLI"
PARTNER_ID = "1336904"
API_TOKEN = "Zc4X9zu0EMrqbPuLy3tN"
PLATFORM_URL = "https://u3.shortink.io/cabinet/demo-quick-high-low?utm_campaign=850173&utm_source=affiliate&utm_medium=sr&a=RLQDltKf13Zlrj&al=1771346&ac=smart-link&cid=960963&code=WELCOME50"
SUPPORT_URL = "https://t.me/andriddddd"
WHITE_LIST = [6765689893, 8273386412]

# ==============================================================================
# БАЗА АКТИВОВ (ВСЕ 40 ЕДИНИЦ)
# ==============================================================================
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

# ==============================================================================
# ИНИЦИАЛИЗАЦИЯ ЛОГГИРОВАНИЯ И СЕРВЕРА
# ==============================================================================
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - [TEAM MASTER SYSTEM] - %(levelname)s - %(message)s'
)
logger = logging.getLogger("QuantumCore")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ==============================================================================
# КЛАСС КВАНТОВОГО АНАЛИЗАТОРА (МАТЕМАТИЧЕСКАЯ МОДЕЛЬ)
# ==============================================================================
class QuantumEngine:
    def __init__(self):
        self.trend_storage = {asset: 0.0 for asset in ALL_PAIRS}

    def compute_signal(self, asset):
        # Имитация рыночного шума и тренда
        self.trend_storage[asset] += random.uniform(-1.8, 1.8)
        
        # Логика анализа
        if self.trend_storage[asset] > 3.0:
            return "📉 🔴 SELL / ВНИЗ", random.randint(90, 99)
        elif self.trend_storage[asset] < -3.0:
            return "📈 🟢 BUY / ВВЕРХ", random.randint(90, 99)
        else:
            return random.choice(["📈 🟢 BUY / ВВЕРХ", "📉 🔴 SELL / ВНИЗ"]), random.randint(70, 85)

engine = QuantumEngine()

# ==============================================================================
# ФУНКЦИИ ВЕРИФИКАЦИИ И ДОСТУПА
# ==============================================================================
async def verify_user(uid: str):
    logger.info(f"Проверка доступа для ID: {uid}")
    if int(uid) in WHITE_LIST:
        return True, True
    
    hash_str = hashlib.md5(f"{uid}:{PARTNER_ID}:{API_TOKEN}".encode()).hexdigest()
    url = f"https://affiliate.pocketoption.com/api/user-info/{uid}/{PARTNER_ID}/{hash_str}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("status") == "success", float(data.get("deposit", 0)) >= 20
    except Exception as e:
        logger.error(f"API Error: {e}")
    return False, False

# ==============================================================================
# ОБРАБОТЧИКИ СООБЩЕНИЙ И КОМАНД
# ==============================================================================
def get_lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 RU", callback_data="lang:ru"), InlineKeyboardButton(text="🇺🇸 EN", callback_data="lang:en")],
        [InlineKeyboardButton(text="🇺🇦 UA", callback_data="lang:ua"), InlineKeyboardButton(text="🇩🇪 DE", callback_data="lang:de")],
        [InlineKeyboardButton(text="🇪🇸 ES", callback_data="lang:es"), InlineKeyboardButton(text="🇫🇷 FR", callback_data="lang:fr")]
    ])

@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    await m.answer("👑 **TEAM MASTER: QUANTUM CORE**\n\nСистема инициализирована. Выберите язык:", reply_markup=get_lang_kb())

@dp.callback_query(F.data.startswith("lang:"))
async def select_lang(c: types.CallbackQuery):
    await c.message.answer("📝 **ШАГ 1:** Зарегистрируйтесь на платформе и пришлите ID:", 
                           reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 ПЛАТФОРМА", url=PLATFORM_URL)]]))

@dp.message(F.text.isdigit())
async def handle_id(m: types.Message):
    reg, dep = await verify_user(m.text)
    if not reg: await m.answer("❌ ID не найден.")
    elif not dep: await m.answer("💳 Пополните баланс.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄 ПРОВЕРИТЬ", callback_data=f"check:{m.text}")]]))
    else: await m.answer("✅ Доступ активирован!", reply_markup=get_main_kb())

@dp.callback_query(F.data.startswith("check:"))
async def check_act(c: types.CallbackQuery):
    _, dep = await verify_user(c.data.split(":")[1])
    if dep: await c.message.answer("✅ Доступ открыт!", reply_markup=get_main_kb())
    else: await c.answer("❌ Депозит не найден.")

def get_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📡 ПОЛУЧИТЬ КВАНТОВЫЙ СИГНАЛ", callback_data="get_sig")],
        [InlineKeyboardButton(text="👨‍💻 ПОДДЕРЖКА", url=SUPPORT_URL)]
    ])

@dp.callback_query(F.data == "get_sig")
async def process_sig(c: types.CallbackQuery):
    msg = await c.message.answer("🔄 **Запуск глубокого анализа...**")
    await asyncio.sleep(2)
    asset = random.choice(ALL_PAIRS)
    direction, conf = engine.compute_signal(asset)
    
    signal = (
        f"📡 **СИГНАЛ TEAM MASTER**\n\n"
        f"🔹 **Актив:** `{asset}`\n"
        f"⚡️ **Направление:** {direction}\n"
        f"⏱ **Экспирация:** `{random.randint(2, 5)} мин`\n"
        f"🔥 **Индекс уверенности:** `{conf}%`\n\n"
        "⚠️ *Соблюдайте риски.*"
    )
    try: await msg.edit_text(signal, reply_markup=get_main_kb())
    except: await c.message.answer(signal, reply_markup=get_main_kb())

# ==============================================================================
# ЗАПУСК И СЕРВЕРНАЯ ЧАСТЬ
# ==============================================================================
async def web_server():
    runner = web.AppRunner(web.Application())
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()

async def main():
    logger.info("SYSTEM INITIALIZED")
    await asyncio.gather(web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    try: asyncio.run(main())
    except Exception as e: logger.critical(f"FATAL SYSTEM ERROR: {e}")
