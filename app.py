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

# --- КОНФИГУРАЦИЯ ---
BOT_TOKEN = "8643698714:AAEh3AdcOKgdhE5NJ4s7ebIAnsM6zGXdkLI"
DB_FILE = "users_db.json"
PARTNER_ID = "1336904"
API_TOKEN = "Zc4X9zu0EMrqbPuLy3tN"
PLATFORM_URL = "https://u3.shortink.io/cabinet/demo-quick-high-low?utm_campaign=850173&utm_source=affiliate&utm_medium=sr&a=RLQDltKf13Zlrj&al=1771346&ac=smart-link&cid=960963&code=WELCOME50"
SUPPORT_URL = "https://t.me/andriddddd"
CHANNEL_URL = "https://t.me/+uekq4TquqkM4Mzcy"

# --- АКТИВЫ ---
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

# --- БАЗА И API ---
def get_db():
    if not os.path.exists(DB_FILE): return {}
    with open(DB_FILE, "r") as f: return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

async def check_user(user_id: str):
    hash_str = hashlib.md5(f"{user_id}:{PARTNER_ID}:{API_TOKEN}".encode()).hexdigest()
    url = f"https://affiliate.pocketoption.com/api/user-info/{user_id}/{PARTNER_ID}/{hash_str}"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("status") == "success", float(data.get("deposit", 0)) >= 20
        except: return False, False
    return False, False

# --- ИНТЕРФЕЙС ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 Платформа", url=PLATFORM_URL), InlineKeyboardButton(text="📢 Канал", url=CHANNEL_URL)],
        [InlineKeyboardButton(text="👨‍💻 Поддержка", url=SUPPORT_URL)],
        [InlineKeyboardButton(text="🔄 Получить сигнал", callback_data="get_sig")]
    ])

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def start(m: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"), InlineKeyboardButton(text="🇺🇸 English", callback_data="lang:en")]
    ])
    await m.answer("👋 Добро пожаловать в TEAM MASTER!\nВыберите язык:", reply_markup=kb)

@dp.callback_query(F.data.startswith("lang:"))
async def select_lang(c: types.CallbackQuery):
    await c.message.answer("📝 Для активации пришлите ваш ID (число):")
    await c.answer()

@dp.message(F.text.isdigit())
async def id_check(m: types.Message):
    is_reg, is_dep = await check_user(m.text)
    if not is_reg:
        await m.answer("❌ ID не найден. Зарегистрируйтесь по ссылке ниже:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Ссылка", url=PLATFORM_URL)]]))
    elif not is_dep:
        await m.answer("💳 Аккаунт найден. Для доступа пополните баланс от $20.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Проверить депозит", callback_data=f"check:{m.text}")]]))
    else:
        await m.answer("✅ Доступ активирован!", reply_markup=get_main_kb())

@dp.callback_query(F.data.startswith("check:"))
async def check_dep(c: types.CallbackQuery):
    _, is_dep = await check_user(c.data.split(":")[1])
    if is_dep: await c.message.answer("✅ Депозит найден! Вы в системе.", reply_markup=get_main_kb())
    else: await c.answer("❌ Депозит не найден.", show_alert=True)

@dp.callback_query(F.data == "get_sig")
async def send_signal(c: types.CallbackQuery):
    msg = await c.message.answer("🔄 Анализирую рынок...")
    await asyncio.sleep(random.uniform(5, 10))
    sig = (f"🚀 **TEAM MASTER СИГНАЛ**\n\n"
           f"📊 Актив: `{random.choice(ALL_PAIRS)}`\n"
           f"⏳ Экспирация: `{random.randint(2, 5)} МИН`\n"
           f"📈 Прогноз: {random.choice(['🟢 ВВЕРХ', '🔴 ВНИЗ'])}\n"
           f"🎯 Точность: `{round(random.uniform(93, 97), 1)}%`")
    await msg.edit_text(sig, reply_markup=get_main_kb())

# --- ЗАПУСК ---
async def web_server():
    runner = web.AppRunner(web.Application())
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.gather(web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
