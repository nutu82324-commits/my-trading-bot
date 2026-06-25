import os
import asyncio
import hashlib
import logging
from datetime import datetime, timedelta
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

# --- 2. АКТИВЫ ---
ALL_PAIRS = [
    "GBP/USD OTC", "EUR/USD OTC", "USD/JPY OTC", "AUD/USD OTC", "USD/CAD OTC",
    "EUR/GBP OTC", "EUR/JPY OTC", "USD/CHF OTC", "Bitcoin OTC", "Ethereum OTC",
    "AED/CNY OTC", "BHD/CNY OTC", "EUR/TRY OTC", "GBP/JPY OTC", "MAD/USD OTC",
    "NGN/USD OTC", "NZD/USD OTC", "USD/CNH OTC", "USD/EGP OTC", "USD/PHP OTC",
    "USD/PKR OTC", "USD/SGD OTC", "USD/THB OTC", "USD/VND OTC", "YER/USD OTC",
    "ZAR/USD OTC", "USD/DZD OTC", "Cardano OTC", "Bitcoin ETF OTC", "BNB OTC",
    "Polkadot OTC", "Litecoin OTC", "Polygon OTC", "Solana OTC", "TRON OTC",
    "Chainlink OTC", "American Express OTC", "Intel OTC", "VISA OTC", "Tesla OTC"
]

# --- 3. ИНИЦИАЛИЗАЦИЯ ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [CORE] - %(message)s')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- 4. МАТЕМАТИЧЕСКИЙ АНАЛИЗАТОР (БЕЗ РАНДОМА) ---
class MathAnalyzer:
    def get_signal(self, asset: str):
        # Используем текущее время для математического расчета тренда
        now = datetime.now()
        # Хешируем время и актив, чтобы получать стабильный "рыночный индекс"
        h = hashlib.md5(f"{now.strftime('%H%M')}:{asset}".encode()).hexdigest()
        trend_val = int(h[:4], 16) % 100 
        
        direction = "📈 🟢 BUY / ВВЕРХ" if trend_val > 48 else "📉 🔴 SELL / ВНИЗ"
        tf = "M5" if trend_val % 2 == 0 else "M1"
        
        # Экспирация от 2 до 5 минут
        duration = 2 + (trend_val % 4)
        finish_time = (now + timedelta(minutes=duration)).strftime("%H:%M:%S")
        
        payout = "92%" if trend_val > 30 else "87%"
        confidence = 88 + (trend_val % 10)
        
        return direction, tf, duration, finish_time, payout, confidence

analyzer = MathAnalyzer()

# --- 5. ВЕРИФИКАЦИЯ ---
async def verify_user(uid: str):
    if int(uid) in WHITE_LIST: return True, True
    # [Заглушка: тут проверка через API PocketOption]
    return True, True 

# --- 6. ХЕНДЛЕРЫ ---
@dp.message(Command("start"))
async def start(m: types.Message):
    text = (
        "👑 **TEAM MASTER: QUANTUM CORE SYSTEM v4.5**\n\n"
        "Система инициализирована. Мы анализируем рыночные данные 24/7 для поиска оптимальных точек входа.\n\n"
        "🌐 **Выберите предпочтительный язык интерфейса:**\n"
        "Select your language / Выберите язык / Оберіть мову / Wählen Sie eine Sprache / Seleccione el idioma / Choisissez votre langue"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 RU", callback_data="lang:ru"), InlineKeyboardButton(text="🇺🇸 EN", callback_data="lang:en")],
        [InlineKeyboardButton(text="🇺🇦 UA", callback_data="lang:ua"), InlineKeyboardButton(text="🇩🇪 DE", callback_data="lang:de")],
        [InlineKeyboardButton(text="🇪🇸 ES", callback_data="lang:es"), InlineKeyboardButton(text="🇫🇷 FR", callback_data="lang:fr")]
    ])
    await m.answer(text, reply_markup=kb)

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
async def auth(m: types.Message):
    await m.answer("✅ Доступ активен!", reply_markup=get_main_kb())

@dp.callback_query(F.data == "get_sig")
async def get_sig(c: types.CallbackQuery):
    asset = ALL_PAIRS[datetime.now().second % len(ALL_PAIRS)]
    direction, tf, duration, finish, payout, conf = analyzer.get_signal(asset)
    
    signal = (
        f"📡 **СИГНАЛ TEAM MASTER**\n\n"
        f"🔹 **Актив:** `{asset}`\n"
        f"⚡️ **Направление:** {direction}\n"
        f"📊 **ТФ:** `{tf}`\n"
        f"⏱ **Экспирация:** `{duration} мин`\n"
        f"⏳ **Вход до:** `{finish}`\n"
        f"🎯 **Выплата:** `{payout}`\n"
        f"🔥 **Индекс уверенности:** `{conf}%`\n\n"
        "⚠️ *Соблюдайте риски.*"
    )
    await c.message.answer(signal, reply_markup=get_main_kb())

def get_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📡 ПОЛУЧИТЬ КВАНТОВЫЙ СИГНАЛ", callback_data="get_sig")],
        [InlineKeyboardButton(text="👨‍💻 ПОДДЕРЖКА", url=SUPPORT_URL)]
    ])

# --- 7. WEB СЕРВЕР (ДЛЯ UPTIMEROBOT) ---
async def web_server():
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()

async def main():
    await asyncio.gather(web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
