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
    reg = State()
    dep = State()
    main = State()
    otc_cat = State()
    otc_asset = State()
    otc_time = State()

# --- КАТАЛОГИ ---
LIVE_PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CAD", "USD/CHF", "AUD/USD", "NZD/USD", "EUR/JPY", "GBP/JPY", "AUD/CAD", "EUR/AUD", "EUR/CAD", "CAD/CHF"]
OTC_CATS = {
    "val": ["AED/CNY OTC", "BHD/CNY OTC", "EUR/GBP OTC", "EUR/TRY OTC", "GBP/JPY OTC", "MAD/USD OTC", "NGN/USD OTC", "NZD/USD OTC", "USD/CNH OTC", "USD/EGP OTC", "USD/PHP OTC", "USD/PKR OTC", "USD/SGD OTC", "USD/THB OTC", "USD/VND OTC", "YER/USD OTC", "ZAR/USD OTC", "USD/CHF OTC", "USD/DZD OTC"],
    "crypto": ["Cardano OTC", "Bitcoin ETF OTC", "BNB OTC", "Polkadot OTC", "Litecoin OTC", "Polygon OTC", "Solana OTC", "TRON OTC", "Chainlink OTC", "Bitcoin OTC"],
    "stock": ["American Express OTC", "FACEBOOK INC OTC", "Intel OTC", "VISA OTC", "Apple OTC", "Pfizer Inc OTC", "Cisco OTC", "Tesla OTC", "Alibaba OTC", "Palantir Technologies OTC"]
}

def get_signal_text(asset, interval, exp):
    finish = (datetime.now() + timedelta(minutes=exp)).strftime("%H:%M:%S")
    return (
        f"📡 **СИГНАЛ TEAM MASTER**\n\n"
        f"🔷 **Актив:** `{asset}`\n"
        f"⚡️ **Направление:** 📈 🟢 BUY / ВВЕРХ\n"
        f"📊 **ТФ:** `{interval}`\n"
        f"⏱ **Экспирация:** `{exp} мин`\n"
        f"⏳ **Вход до:** `{finish}`\n"
        f"🎯 **Выплата:** `{random.randint(90, 96)}%`\n"
        f"🔥 **Индекс уверенности:** `{random.randint(93, 98)}%`\n\n"
        "⚠️ *Соблюдайте риски.*"
    )

@dp.message(Command("start"))
async def start(m: types.Message, state: FSMContext):
    text = ("👑 **TEAM MASTER: QUANTUM CORE SYSTEM v4.5**\n\n"
            "Система инициализована. Мы анализируем рыночные данные 24/7.\n\n"
            "🌐 **Выберите язык:**")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 RU", callback_data="lang"), InlineKeyboardButton(text="🇺🇸 EN", callback_data="lang")],
        [InlineKeyboardButton(text="🇺🇦 UA", callback_data="lang"), InlineKeyboardButton(text="🇩🇪 DE", callback_data="lang")],
        [InlineKeyboardButton(text="🇪🇸 ES", callback_data="lang"), InlineKeyboardButton(text="🇫🇷 FR", callback_data="lang")]
    ])
    await m.answer(text, reply_markup=kb)
    await state.set_state(Flow.reg)

@dp.callback_query(F.data == "lang")
async def lang_choice(c: types.CallbackQuery):
    await c.message.edit_text("📝 **ШАГ 1: РЕГИСТРАЦИЯ**\nПришлите ID:", 
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 ПЕРЕЙТИ НА ПЛАТФОРМУ", url=PLATFORM_URL)]]))

@dp.message(Flow.reg)
async def check_id(m: types.Message, state: FSMContext):
    if m.text.isdigit() and int(m.text) in WHITE_LIST:
        await m.answer("✅ **ID принят. ШАГ 2: Пополнение от $20.** (Пришлите сумму/скрин)")
        await state.set_state(Flow.dep)

@dp.message(Flow.dep)
async def check_dep(m: types.Message, state: FSMContext):
    if m.text.isdigit() and int(m.text) >= 20:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🤖 АВТО-РЕЖИМ", callback_data="mode:auto")],
            [InlineKeyboardButton(text="🌍 ЖИВОЙ РЫНОК", callback_data="mode:live")],
            [InlineKeyboardButton(text="💎 OTC РЫНОК", callback_data="mode:otc")]
        ])
        await m.answer("✅ **Доступ открыт. Выберите режим:**", reply_markup=kb)
        await state.set_state(Flow.main)

@dp.callback_query(F.data == "mode:auto")
async def auto_mode(c: types.CallbackQuery):
    await c.message.answer(get_signal_text(random.choice(LIVE_PAIRS), "M1", random.randint(2, 5)))

@dp.callback_query(F.data == "mode:live")
async def live_mode(c: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=p, callback_data=f"sig:{p}")] for p in LIVE_PAIRS[:5]])
    await c.message.answer("🌍 Выберите актив:", reply_markup=kb)

@dp.callback_query(F.data.startswith("sig:"))
async def send_sig(c: types.CallbackQuery):
    asset = c.data.split(":")[1]
    await c.message.answer(get_signal_text(asset, "M1", random.randint(2, 5)))

@dp.callback_query(F.data == "mode:otc")
async def otc_cat(c: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 Валюта", callback_data="cat:val")],
        [InlineKeyboardButton(text="🪙 Крипта", callback_data="cat:crypto")],
        [InlineKeyboardButton(text="📊 Акции", callback_data="cat:stock")]
    ])
    await c.message.edit_text("📂 Выберите категорию:", reply_markup=kb)
    await state.set_state(Flow.otc_cat)

@dp.callback_query(F.data.startswith("cat:"))
async def otc_list(c: types.CallbackQuery, state: FSMContext):
    cat = c.data.split(":")[1]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=a, callback_data=f"asset:{a}")] for a in OTC_CATS[cat]])
    await c.message.edit_text("🔹 Выберите актив:", reply_markup=kb)
    await state.set_state(Flow.otc_asset)

@dp.callback_query(F.data.startswith("asset:"))
async def set_time(c: types.CallbackQuery, state: FSMContext):
    asset = c.data.split(":")[1]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{i} сек", callback_data=f"fin:{asset}:{i}")] for i in [5, 30, 60, 300]
    ])
    await c.message.edit_text("⏳ Выберите интервал:", reply_markup=kb)
    await state.set_state(Flow.otc_time)

@dp.callback_query(F.data.startswith("fin:"))
async def final_otc(c: types.CallbackQuery):
    _, asset, t = c.data.split(":")
    await c.message.answer(get_signal_text(asset, f"{t} сек", random.randint(2, 5)))

async def main():
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
