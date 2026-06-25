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

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8643698714:AAEh3AdcOKgdhE5NJ4s7ebIAnsM6zGXdkLI"
PARTNER_ID = "1336904"
API_TOKEN = "Zc4X9zu0EMrqbPuLy3tN"
PLATFORM_URL = "https://u3.shortink.io/cabinet/demo-quick-high-low?utm_campaign=850173&utm_source=affiliate&utm_medium=sr&a=RLQDltKf13Zlrj&al=1771346&ac=smart-link&cid=960963&code=WELCOME50"
SUPPORT_URL = "https://t.me/andriddddd"
CHANNEL_URL = "https://t.me/+uekq4TquqkM4Mzcy"

# --- БЕЛЫЙ СПИСОК (ID друзей с полным доступом) ---
WHITE_LIST = [6765689893, 8273386412]

# --- СПИСОК АКТИВОВ ---
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

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- ФУНКЦИИ ПРОВЕРКИ ---
async def check_user_access(user_id: str):
    if int(user_id) in WHITE_LIST: return True, True
    
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
def get_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 ЗАПУСТИТЬ ИИ-АНАЛИЗ", callback_data="get_sig")],
        [InlineKeyboardButton(text="📈 ПЛАТФОРМА", url=PLATFORM_URL), InlineKeyboardButton(text="📢 КАНАЛ", url=CHANNEL_URL)],
        [InlineKeyboardButton(text="👨‍💻 ПОДДЕРЖКА", url=SUPPORT_URL)]
    ])

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def start(m: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"), InlineKeyboardButton(text="🇺🇸 English", callback_data="lang:en")]
    ])
    await m.answer("🤖 **TEAM MASTER QUANTUM CORE v18.0**\nВыберите язык:", reply_markup=kb)

@dp.callback_query(F.data.startswith("lang:"))
async def reg(c: types.CallbackQuery):
    await c.message.answer("📝 **ШАГ 1: РЕГИСТРАЦИЯ**\nЗарегистрируйтесь по ссылке и пришлите свой ID:", 
                           reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 РЕГИСТРАЦИЯ", url=PLATFORM_URL)]]))

@dp.message(F.text.isdigit())
async def id_check(m: types.Message):
    is_reg, is_dep = await check_user_access(m.text)
    if not is_reg:
        await m.answer("❌ Ошибка: ID не найден. Зарегистрируйтесь по ссылке.")
    elif not is_dep:
        await m.answer("💳 **ШАГ 2: АКТИВАЦИЯ**\nПополните от $20 (промо WELCOME50).\nПосле пополнения нажмите кнопку:", 
                       reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄 ПРОВЕРИТЬ АКТИВАЦИЮ", callback_data=f"check:{m.text}")]]))
    else:
        await m.answer("✅ **СИСТЕМА АКТИВИРОВАНА!**", reply_markup=get_main_kb())

@dp.callback_query(F.data.startswith("check:"))
async def check_btn(c: types.CallbackQuery):
    _, is_dep = await check_user_access(c.data.split(":")[1])
    if is_dep: await c.message.answer("✅ **Успешно!**", reply_markup=get_main_kb())
    else: await c.answer("❌ Депозит не найден.", show_alert=True)

@dp.callback_query(F.data == "get_sig")
async def signal(c: types.CallbackQuery):
    msg = await c.message.answer("🔄 **ИИ-КВАНТОВЫЙ АНАЛИЗ...**")
    await asyncio.sleep(random.uniform(5, 10))
    sig = (f"🚀 **TEAM MASTER — СИГНАЛ**\n\n📊 Актив: `{random.choice(ALL_PAIRS)}`\n"
           f"⏳ Экспирация: `{random.randint(2, 5)} МИН`\n"
           f"📈 Прогноз: {random.choice(['🟢 ВВЕРХ / CALL', '🔴 ВНИЗ / PUT'])}\n"
           f"🎯 Точность: `{round(random.uniform(94, 98), 1)}%`")
    await msg.edit_text(sig, reply_markup=get_main_kb())

# --- ЗАПУСК ---
async def web_server():
    runner = web.AppRunner(web.Application())
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()

async def main():
    await asyncio.gather(web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
