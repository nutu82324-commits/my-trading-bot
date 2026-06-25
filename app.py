import asyncio
import random
import os
from aiohttp import web
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# --- КОНФИГУРАЦИЯ ---
BOT_TOKEN = "8643698714:AAG9xjwn1kNBd6faJw34Xso6Gdm3ClvE2tc"
WHITE_LIST = [6765689893, 8273386412]
SUPPORT_URL = "https://t.me/andriddddd"
PLATFORM_URL = "https://u3.shortink.io/cabinet/demo-quick-high-low?utm_campaign=850173&utm_source=affiliate&utm_medium=sr&a=RLQDltKf13Zlrj&al=1771346&ac=smart-link&cid=960963&code=WELCOME50"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Flow(StatesGroup):
    language = State()
    registration = State()
    deposit = State()
    main = State()

# --- АКТИВЫ ---
ALL_ASSETS = [
    "AED/CNY OTC", "BHD/CNY OTC", "EUR/GBP OTC", "EUR/TRY OTC", "GBP/JPY OTC", "MAD/USD OTC", 
    "NGN/USD OTC", "NZD/USD OTC", "USD/CNH OTC", "USD/EGP OTC", "USD/PHP OTC", "USD/PKR OTC", 
    "USD/SGD OTC", "USD/THB OTC", "USD/VND OTC", "YER/USD OTC", "ZAR/USD OTC", "USD/CHF OTC", 
    "USD/DZD OTC", "Cardano OTC", "Bitcoin ETF OTC", "BNB OTC", "Polkadot OTC", "Litecoin OTC", 
    "Polygon OTC", "Solana OTC", "TRON OTC", "Chainlink OTC", "Bitcoin OTC", "American Express OTC", 
    "FACEBOOK INC OTC", "Intel OTC", "VISA OTC", "Apple OTC", "Pfizer Inc OTC", "Cisco OTC", 
    "Tesla OTC", "Alibaba OTC", "Palantir Technologies OTC", "EUR/USD", "GBP/USD", "USD/JPY"
]

def get_signal_text(asset):
    exp = random.randint(2, 5)
    finish = (datetime.now() + timedelta(minutes=exp)).strftime("%H:%M:%S")
    return (
        f"📡 **СИГНАЛ TEAM MASTER**\n\n"
        f"🔷 **Актив:** `{asset}`\n"
        f"⚡️ **Направление:** 📈 🟢 BUY / ВВЕРХ\n"
        f"📊 **ТФ:** `M1`\n"
        f"⏱ **Экспирация:** `{exp} мин`\n"
        f"⏳ **Вход до:** `{finish}`\n"
        f"🎯 **Выплата:** `{random.randint(90, 96)}%`\n"
        f"🔥 **Индекс уверенности:** `{random.randint(93, 98)}%`\n\n"
        "⚠️ *Соблюдайте риски.*"
    )

# --- ЛОГИКА ---
@dp.message(Command("start"))
async def start(m: types.Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 RU", callback_data="lang"), InlineKeyboardButton(text="🇺🇸 EN", callback_data="lang")],
        [InlineKeyboardButton(text="🇺🇦 UA", callback_data="lang"), InlineKeyboardButton(text="🇩🇪 DE", callback_data="lang")],
        [InlineKeyboardButton(text="🇪🇸 ES", callback_data="lang"), InlineKeyboardButton(text="🇫🇷 FR", callback_data="lang")]
    ])
    await m.answer("👑 **TEAM MASTER: QUANTUM CORE SYSTEM v4.5**\n\n🌐 **Выберите язык:**", reply_markup=kb)
    await state.set_state(Flow.language)

@dp.callback_query(F.data == "lang")
async def lang_choice(c: types.CallbackQuery, state: FSMContext):
    await c.message.edit_text("📝 **ШАГ 1: РЕГИСТРАЦИЯ**\nПришлите ваш ID после регистрации:", 
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 ПЕРЕЙТИ", url=PLATFORM_URL)]]))
    await state.set_state(Flow.registration)

@dp.message(Flow.registration)
async def reg_id(m: types.Message, state: FSMContext):
    if m.text.isdigit() and int(m.text) in WHITE_LIST:
        await m.answer("✅ **ID принят. ШАГ 2: Пополнение от $20.** Пришлите сумму или скриншот:")
        await state.set_state(Flow.deposit)
    else:
        await m.answer("❌ **Ошибка: ID не найден.**")

@dp.message(Flow.deposit)
async def check_dep(m: types.Message, state: FSMContext):
    if m.text.isdigit() and int(m.text) >= 20:
        await m.answer("✅ **Депозит подтвержден!**", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📡 ПОЛУЧИТЬ КВАНТОВЫЙ СИГНАЛ", callback_data="get_sig")],
            [InlineKeyboardButton(text="👨‍💻 ПОДДЕРЖКА", url=SUPPORT_URL)]
        ]))
        await state.set_state(Flow.main)
    else:
        await m.answer("❌ **Ошибка: Минимальный депозит $20.**")

@dp.callback_query(F.data == "get_sig")
async def send_sig(c: types.CallbackQuery):
    await c.message.answer(get_signal_text(random.choice(ALL_ASSETS)), reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📡 ПОЛУЧИТЬ КВАНТОВЫЙ СИГНАЛ", callback_data="get_sig")],
        [InlineKeyboardButton(text="👨‍💻 ПОДДЕРЖКА", url=SUPPORT_URL)]
    ]))

# --- ЗАПУСК ---
async def start_bot():
    # Запуск веб-сервера (для Render)
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="Bot is running!"))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())
