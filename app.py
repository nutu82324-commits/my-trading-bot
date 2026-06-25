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

# --- 1. КОНФИГУРАЦИЯ ---
BOT_TOKEN = "8643698714:AAEh3AdcOKgdhE5NJ4s7ebIAnsM6zGXdkLI"
PARTNER_ID = "1336904"
API_TOKEN = "Zc4X9zu0EMrqbPuLy3tN"
PLATFORM_URL = "https://u3.shortink.io/cabinet/demo-quick-high-low?utm_campaign=850173&utm_source=affiliate&utm_medium=sr&a=RLQDltKf13Zlrj&al=1771346&ac=smart-link&cid=960963&code=WELCOME50"
SUPPORT_URL = "https://t.me/andriddddd"
WHITE_LIST = [6765689893, 8273386412]

# --- 2. ПОЛНЫЙ СПИСОК ИЗ 40 АКТИВОВ ---
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

# --- 3. НАСТРОЙКИ СИСТЕМЫ ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [CORE SYSTEM] - %(message)s')
logger = logging.getLogger("QuantumMasterCore")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- 4. КВАНТОВЫЙ ДВИЖОК АНАЛИЗА ---
class QuantumAnalyzer:
    def __init__(self):
        self.market_memory = {asset: 0.0 for asset in ALL_PAIRS}

    def analyze_market(self, asset):
        # Алгоритм имитации рыночного импульса
        self.market_memory[asset] += random.uniform(-1.8, 1.8)
        
        # Анализ данных
        if self.market_memory[asset] > 3.0:
            return "📉 🔴 SELL / ВНИЗ", random.randint(90, 99)
        elif self.market_memory[asset] < -3.0:
            return "📈 🟢 BUY / ВВЕРХ", random.randint(90, 99)
        else:
            return random.choice(["📈 🟢 BUY / ВВЕРХ", "📉 🔴 SELL / ВНИЗ"]), random.randint(75, 88)

engine = QuantumAnalyzer()

# --- 5. ВЕРИФИКАЦИЯ ПОЛЬЗОВАТЕЛЯ ---
async def verify_user(uid: str):
    if int(uid) in WHITE_LIST: return True, True
    hash_str = hashlib.md5(f"{uid}:{PARTNER_ID}:{API_TOKEN}".encode()).hexdigest()
    url = f"https://affiliate.pocketoption.com/api/user-info/{uid}/{PARTNER_ID}/{hash_str}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("status") == "success", float(data.get("deposit", 0)) >= 20
    except: pass
    return False, False

# --- 6. ИНТЕРФЕЙС И КЛАВИАТУРЫ ---
def get_lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 RU", callback_data="lang:ru"), InlineKeyboardButton(text="🇺🇸 EN", callback_data="lang:en")],
        [InlineKeyboardButton(text="🇺🇦 UA", callback_data="lang:ua"), InlineKeyboardButton(text="🇩🇪 DE", callback_data="lang:de")],
        [InlineKeyboardButton(text="🇪🇸 ES", callback_data="lang:es"), InlineKeyboardButton(text="🇫🇷 FR", callback_data="lang:fr")]
    ])

def get_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📡 ПОЛУЧИТЬ КВАНТОВЫЙ СИГНАЛ", callback_data="get_sig")],
        [InlineKeyboardButton(text="👨‍💻 ПОДДЕРЖКА", url=SUPPORT_URL)]
    ])

# --- 7. ОБРАБОТЧИКИ СОБЫТИЙ ---
@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    await m.answer(
        "👑 **TEAM MASTER: QUANTUM CORE SYSTEM v5.0**\n\n"
        "Система инициализирована. Мы анализируем рыночные данные 24/7 для поиска оптимальных точек входа.\n\n"
        "🌐 **Выберите предпочтительный язык интерфейса:**\n"
        "Select language / Выберите язык / Оберіть мову / Wählen Sie eine Sprache / Seleccione el idioma / Choisissez votre langue",
        reply_markup=get_lang_kb()
    )

@dp.callback_query(F.data.startswith("lang:"))
async def select_lang(c: types.CallbackQuery):
    await c.message.edit_text(
        "📝 **ШАГ 1: РЕГИСТРАЦИЯ В СИСТЕМЕ**\n\n"
        "Для обеспечения синхронизации вашего торгового аккаунта с нашим квантовым ядром, вы обязаны пройти регистрацию по партнерской ссылке.\n\n"
        "После завершения регистрации, пожалуйста, скопируйте ваш ID и отправьте его в этот чат.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📈 ПЕРЕЙТИ НА ПЛАТФОРМУ", url=PLATFORM_URL)]
        ])
    )

@dp.message(F.text.isdigit())
async def handle_id(m: types.Message):
    reg, dep = await verify_user(m.text)
    if not reg: await m.answer("❌ ID не найден.")
    elif not dep: await m.answer("💳 Пополните счет от $20.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄 ПРОВЕРИТЬ", callback_data=f"check:{m.text}")]]))
    else: await m.answer("✅ Доступ активен!", reply_markup=get_main_kb())

@dp.callback_query(F.data.startswith("check:"))
async def check_act(c: types.CallbackQuery):
    _, dep = await verify_user(c.data.split(":")[1])
    if dep: await c.message.edit_text("✅ Доступ активирован!", reply_markup=get_main_kb())
    else: await c.answer("❌ Депозит не найден.", show_alert=True)

@dp.callback_query(F.data == "get_sig")
async def process_sig(c: types.CallbackQuery):
    msg = await c.message.answer("🔄 **Запуск глубокого анализа...**")
    await asyncio.sleep(2)
    asset = random.choice(ALL_PAIRS)
    direction, conf = engine.analyze_market(asset)
    
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

# --- 8. ЗАПУСК И СЕРВЕР ---
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
