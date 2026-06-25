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

# --- ВСЕ АКТИВЫ ---
CURRENCIES = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CAD", "USD/CHF", "AUD/USD", "NZD/USD"]
CROSS_PAIRS = ["EUR/JPY", "GBP/JPY", "AUD/CAD", "EUR/AUD", "EUR/CAD", "CAD/CHF"]
OTC = [
    "AED/CNY OTC", "BHD/CNY OTC", "EUR/GBP OTC", "EUR/TRY OTC", "GBP/JPY OTC", "MAD/USD OTC", 
    "NGN/USD OTC", "NZD/USD OTC", "USD/CNH OTC", "USD/EGP OTC", "USD/PHP OTC", "USD/PKR OTC", 
    "USD/SGD OTC", "USD/THB OTC", "USD/VND OTC", "YER/USD OTC", "ZAR/USD OTC", "USD/CHF OTC", 
    "USD/DZD OTC", "Cardano OTC", "Bitcoin ETF OTC", "BNB OTC", "Polkadot OTC", "Litecoin OTC", 
    "Polygon OTC", "Solana OTC", "TRON OTC", "Chainlink OTC", "Bitcoin OTC", "American Express OTC", 
    "FACEBOOK INC OTC", "Intel OTC", "VISA OTC", "Apple OTC", "Pfizer Inc OTC", "Cisco OTC", 
    "Tesla OTC", "Alibaba OTC", "Palantir Technologies OTC"
]

def get_lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 RU", callback_data="lang"), InlineKeyboardButton(text="🇺🇸 EN", callback_data="lang")],
        [InlineKeyboardButton(text="🇺🇦 UA", callback_data="lang"), InlineKeyboardButton(text="🇩🇪 DE", callback_data="lang")],
        [InlineKeyboardButton(text="🇪🇸 ES", callback_data="lang"), InlineKeyboardButton(text="🇫🇷 FR", callback_data="lang")]
    ])

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

@dp.message(Command("start"))
async def start(m: types.Message, state: FSMContext):
    msg = ("👑 **TEAM MASTER: QUANTUM CORE SYSTEM v4.5**\n\n"
           "Система инициализована. Мы анализируем рыночные данные 24/7 для поиска оптимальных точек входа.\n\n"
           "🌐 **Выберите предпочтительный язык интерфейса:**")
    await m.answer(msg, reply_markup=get_lang_kb())
    await state.set_state(Flow.language)

@dp.callback_query(F.data == "lang")
async def lang_choice(c: types.CallbackQuery, state: FSMContext):
    await c.message.edit_text("📝 **ШАГ 1: РЕГИСТРАЦИЯ В СИСТЕМЕ**\n\n"
                             "Для обеспечения синхронизации вашего торгового аккаунта с нашим квантовым ядром, "
                             "вы обязаны пройти регистрацию по партнерской ссылке.\n\n"
                             "После завершения регистрации, пожалуйста, скопируйте ваш ID и отправьте его в этот чат.", 
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 ПЕРЕЙТИ НА ПЛАТФОРМУ", url=PLATFORM_URL)]]))
    await state.set_state(Flow.registration)

@dp.message(Flow.registration)
async def check_id(m: types.Message, state: FSMContext):
    if m.text.isdigit() and int(m.text) in WHITE_LIST:
        await m.answer("✅ **Синхронизация успешна. ШАГ 2: Пополните счет от $20.**\nПришлите сумму или скриншот пополнения:")
        await state.set_state(Flow.deposit)
    else:
        await m.answer("❌ **Ошибка: ID не верифицирован в системе.**")

@dp.message(Flow.deposit)
async def check_dep(m: types.Message, state: FSMContext):
    if m.text.isdigit() and int(m.text) >= 20:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📡 ПОЛУЧИТЬ КВАНТОВЫЙ СИГНАЛ", callback_data="get_sig")],
            [InlineKeyboardButton(text="👨‍💻 ПОДДЕРЖКА", url=SUPPORT_URL)]
        ])
        await m.answer("✅ **Депозит подтвержден. Ядро квантовой сети активно.**", reply_markup=kb)
        await state.set_state(Flow.main)
    else:
        await m.answer("❌ **Ошибка: Минимальный депозит для активации ядра — $20.**")

@dp.callback_query(F.data == "get_sig")
async def send_sig(c: types.CallbackQuery):
    all_assets = CURRENCIES + CROSS_PAIRS + OTC
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📡 ПОЛУЧИТЬ КВАНТОВЫЙ СИГНАЛ", callback_data="get_sig")],
        [InlineKeyboardButton(text="👨‍💻 ПОДДЕРЖКА", url=SUPPORT_URL)]
    ])
    await c.message.answer(get_signal_text(random.choice(all_assets)), reply_markup=kb)

async def start_web():
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="Bot is running!"))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start_web())
    loop.run_until_complete(dp.start_polling(bot))
