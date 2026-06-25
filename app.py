import asyncio
import random
import os
import aiohttp
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# --- КОНФИГ ---
BOT_TOKEN = "8643698714:AAG9xjwn1kNBd6faJw34Xso6Gdm3ClvE2tc"
API_KEY = "YOUR_PARTNER_API_KEY"
PLATFORM_API_URL = "https://api.your-platform.com/check_deposit"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- ДАННЫЕ РЫНКОВ ---
LIVE_MARKET = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CAD", "USD/CHF", "AUD/USD", "NZD/USD", "EUR/JPY", "GBP/JPY", "AUD/CAD", "EUR/AUD", "EUR/CAD", "CAD/CHF"]
OTC_DATA = {
    "val": ["AED/CNY OTC", "BHD/CNY OTC", "EUR/GBP OTC", "EUR/TRY OTC", "GBP/JPY OTC", "MAD/USD OTC", "NGN/USD OTC", "NZD/USD OTC", "USD/CNH OTC", "USD/EGP OTC", "USD/PHP OTC", "USD/PKR OTC", "USD/SGD OTC", "USD/THB OTC", "USD/VND OTC", "YER/USD OTC", "ZAR/USD OTC", "USD/CHF OTC", "USD/DZD OTC"],
    "crypto": ["Cardano OTC", "Bitcoin ETF OTC", "BNB OTC", "Polkadot OTC", "Litecoin OTC", "Polygon OTC", "Solana OTC", "TRON OTC", "Chainlink OTC", "Bitcoin OTC"],
    "stock": ["American Express OTC", "FACEBOOK INC OTC", "Intel OTC", "VISA OTC", "Apple OTC", "Pfizer Inc OTC", "Cisco OTC", "Tesla OTC", "Alibaba OTC", "Palantir Technologies OTC"]
}

class Flow(StatesGroup):
    reg = State()
    main = State()
    market = State()
    cat = State()
    asset = State()
    interval = State()
    exp = State()

async def check_api(user_id):
    # Логика запроса к API платформы
    return True # Замени на реальную проверку

def get_signal(asset, tf, exp):
    return (f"📡 **СИГНАЛ TEAM MASTER**\n\n"
            f"🔷 **Актив:** `{asset}`\n"
            f"⚡️ **Направление:** 📈 🟢 BUY / ВВЕРХ\n"
            f"📊 **ТФ:** `{tf}`\n"
            f"⏱ **Экспирация:** `{exp}`\n"
            f"⏳ **Вход до:** {(asyncio.get_event_loop().time() + 300):.0f}\n"
            f"🎯 **Выплата:** `{random.randint(90, 96)}%`\n"
            f"🔥 **Индекс уверенности:** `{random.randint(93, 98)}%`\n\n"
            "⚠️ *Соблюдайте риски.*")

# --- ХЕНДЛЕРЫ ---
@dp.message(Command("start"))
async def start(m: types.Message, state: FSMContext):
    await m.answer("👑 **TEAM MASTER: QUANTUM CORE v4.5**\n\nВыберите язык:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 RU", callback_data="lang"), InlineKeyboardButton(text="🇺🇸 EN", callback_data="lang")]
    ]))
    await state.set_state(Flow.reg)

@dp.callback_query(F.data == "lang")
async def ask_id(c: types.CallbackQuery):
    await c.message.edit_text("📝 **ШАГ 1: Введите ID:**", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 ПЕРЕЙТИ", url="https://u3.shortink.io/cabinet/demo-quick-high-low?a=RLQDltKf13Zlrj")]]))

@dp.message(Flow.reg)
async def verify(m: types.Message, state: FSMContext):
    if await check_api(m.text):
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🤖 Автомат", callback_data="mode:auto"), InlineKeyboardButton(text="⚙️ Ручной", callback_data="mode:manual")]])
        await m.answer("✅ **Успешно. Выберите режим:**", reply_markup=kb)
        await state.set_state(Flow.main)
    else:
        await m.answer("❌ **Депозит не найден.**")

@dp.callback_query(F.data == "mode:auto")
async def auto(c: types.CallbackQuery):
    await c.message.answer(get_signal(random.choice(LIVE_MARKET), "M1", f"{random.randint(2, 5)} мин"))

@dp.callback_query(F.data == "mode:manual")
async def manual(c: types.CallbackQuery, state: FSMContext):
    await c.message.edit_text("Выберите рынок:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌍 Живой", callback_data="m:live")], [InlineKeyboardButton(text="💎 OTC", callback_data="m:otc")]]))
    await state.set_state(Flow.market)

@dp.callback_query(F.data == "m:otc")
async def otc_cat(c: types.CallbackQuery, state: FSMContext):
    await c.message.edit_text("Категория:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 Валюта", callback_data="c:val")], [InlineKeyboardButton(text="🪙 Крипта", callback_data="c:crypto")]]))
    await state.set_state(Flow.cat)

@dp.callback_query(F.data.startswith("c:"))
async def choose_asset(c: types.CallbackQuery, state: FSMContext):
    cat = c.data.split(":")[1]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=a, callback_data=f"a:{a}")] for a in OTC_DATA[cat]])
    await c.message.edit_text("Актив:", reply_markup=kb)
    await state.set_state(Flow.asset)

@dp.callback_query(F.data.startswith("a:"))
async def choose_tf(c: types.CallbackQuery, state: FSMContext):
    await state.update_data(asset=c.data.split(":")[1])
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=i, callback_data=f"i:{i}")] for i in ["5 сек", "30 сек", "1 мин", "5 мин"]])
    await c.message.edit_text("Интервал свечи:", reply_markup=kb)
    await state.set_state(Flow.interval)

@dp.callback_query(F.data.startswith("i:"))
async def choose_exp(c: types.CallbackQuery, state: FSMContext):
    await state.update_data(tf=c.data.split(":")[1])
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=e, callback_data=f"e:{e}")] for e in ["30 сек", "1 мин", "5 мин"]])
    await c.message.edit_text("Экспирация:", reply_markup=kb)
    await state.set_state(Flow.exp)

@dp.callback_query(F.data.startswith("e:"))
async def final(c: types.CallbackQuery, state: FSMContext):
    d = await state.get_data()
    await c.message.answer(get_signal(d['asset'], d['tf'], c.data.split(":")[1]))

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
