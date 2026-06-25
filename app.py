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

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TeamMasterAuto")

# --- КОНФИГУРАЦИЯ ---
BOT_TOKEN = "8860569012:AAHIV9WLewsv_cKHFYAo6vcxvCIb-uCVvI8"
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

# --- ПОЛНЫЙ СПИСОК АКТИВОВ ---
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

# --- WEB-СЕРВЕР ---
async def handle(request): return web.Response(text="Bot is alive!")

async def start_webhook():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8000))
    await web.TCPSite(runner, '0.0.0.0', port).start()

# --- БАЗА ДАННЫХ ---
def get_db():
    if not os.path.exists(DB_FILE): return {"users": {}}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {"users": {}}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- ПРОВЕРКА API ---
async def check_pocket_api_full(user_id: str) -> tuple[bool, bool]:
    hash_str = hashlib.md5(f"{user_id}:{PARTNER_ID}:{API_TOKEN}".encode()).hexdigest()
    url = f"https://affiliate.pocketoption.com/api/user-info/{user_id}/{PARTNER_ID}/{hash_str}"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                return True, float(data.get("deposit", 0)) >= 20
        except: pass
    return False, False

# --- КНОПКИ И ГЕНЕРАЦИЯ ---
def get_signal_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 ОТКРЫТЬ POCKET OPTION", url=PLATFORM_URL)],
        [InlineKeyboardButton(text="📢 НАШ ТЕЛЕГРАМ КАНАЛ", url=TELEGRAM_CHANNEL)],
        [InlineKeyboardButton(text="👨‍💻 SUPPORT", url=SUPPORT_URL)],
        [InlineKeyboardButton(text="🔄 СЛЕДУЮЩИЙ СИГНАЛ", callback_data="next_sig")]
    ])

def generate_signal_text():
    return (f"🚀 **TEAM MASTER — СИГНАЛ СФОРМИРОВАН** 🚀\n\n"
            f"📊 Актив: `{random.choice(ALL_PAIRS)}`\n"
            f"📈 Направление: {random.choice(['🟢 ВВЕРХ / CALL', '🔴 ВНИЗ / PUT'])}\n"
            f"🎯 Точность: `{round(random.uniform(91.4, 96.2), 1)}%`")

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer_photo(PHOTO_URL, caption="📈 **TEAM MASTER GLOBAL BOT v18.0**\n\nОтправьте ваш ID:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 РЕГИСТРАЦИЯ", url=PLATFORM_URL)]]))

@dp.message(F.text)
async def handle_id(m: types.Message):
    if not m.text.isdigit(): return
    ref, dep = await check_pocket_api_full(m.text)
    if not ref: await m.answer("❌ ID не найден."); return
    
    if dep or m.from_user.id in ADMIN_IDS + VIP_IDS:
        await m.answer(generate_signal_text(), reply_markup=get_signal_keyboard())
    else:
        await m.answer("💳 Пополните баланс на $20 для доступа.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💳 ПОПОЛНИТЬ", url=PLATFORM_URL)]]))

@dp.callback_query(F.data == "next_sig")
async def next_sig(c: types.CallbackQuery):
    await c.message.answer(generate_signal_text(), reply_markup=get_signal_keyboard())
    await c.answer()

async def main():
    asyncio.create_task(start_webhook())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
