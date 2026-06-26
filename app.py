import asyncio
import random
import os
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8643698714:AAF0ucnrgpNHzlD1G6dD7FZXVk5Jm6jpxUM"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- ДАННЫЕ ---
LIVE = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CAD", "USD/CHF", "AUD/USD", "NZD/USD", "EUR/JPY", "GBP/JPY", "AUD/CAD", "EUR/AUD", "EUR/CAD", "CAD/CHF"]
OTC_DATA = {
    "val": ["AED/CNY OTC", "BHD/CNY OTC", "EUR/GBP OTC", "EUR/TRY OTC", "GBP/JPY OTC", "MAD/USD OTC", "NGN/USD OTC", "NZD/USD OTC", "USD/CNH OTC", "USD/EGP OTC", "USD/PHP OTC", "USD/PKR OTC", "USD/SGD OTC", "USD/THB OTC", "USD/VND OTC", "YER/USD OTC", "ZAR/USD OTC", "USD/CHF OTC", "USD/DZD OTC"],
    "crypto": ["Cardano OTC", "Bitcoin ETF OTC", "BNB OTC", "Polkadot OTC", "Litecoin OTC", "Polygon OTC", "Solana OTC", "TRON OTC", "Chainlink OTC", "Bitcoin OTC"],
    "stock": ["American Express OTC", "FACEBOOK INC OTC", "Intel OTC", "VISA OTC", "Apple OTC", "Pfizer Inc OTC", "Cisco OTC", "Tesla OTC", "Alibaba OTC", "Palantir Technologies OTC"]
}

class FSM(StatesGroup):
    reg = State()
    mode = State()
    market = State()
    cat = State()
    asset = State()
    tf = State()
    exp = State()

# --- ФУНКЦИИ ---
async def get_signal_text(asset, tf, exp):
    direction = random.choice([("🟢 BUY / ВВЕРХ", "📈"), ("🔴 SELL / ВНИЗ", "📉")])
    dir_text, dir_icon = direction
    
    text = (f"📡 **СИГНАЛ TEAM MASTER**\n\n"
            f"🔷 **Актив:** `{asset}`\n"
            f"⚡️ **Направление:** {dir_icon} {dir_text}\n"
            f"📊 **ТФ:** `{tf}`\n"
            f"⏱ **Экспирация:** `{exp}`\n"
            f"⏳ **Вход до:** {(asyncio.get_event_loop().time() + 300):.0f}\n"
            f"🎯 **Выплата:** `{random.randint(90, 96)}%`\n"
            f"🔥 **Индекс уверенности:** `{random.randint(93, 98)}%`\n\n"
            "⚠️ *Соблюдайте риски.*")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📡 ПОЛУЧИТЬ КВАНТОВЫЙ СИГНАЛ", callback_data="m:auto")],
        [InlineKeyboardButton(text="👤 ПОДДЕРЖКА", url="https://t.me/support_link")]
    ])
    return text, kb

# --- ХЕНДЛЕРЫ ---
@dp.message(Command("start"))
async def start(m: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 RU", callback_data="lang"), InlineKeyboardButton(text="🇺🇸 EN", callback_data="lang")],
        [InlineKeyboardButton(text="🇺🇦 UA", callback_data="lang"), InlineKeyboardButton(text="🇩🇪 DE", callback_data="lang")]
    ])
    await m.answer("👑 **TEAM MASTER: QUANTUM CORE SYSTEM v4.5**\n\nСистема инициализирована. Выберите язык:", reply_markup=kb)

@dp.callback_query(F.data == "lang")
async def reg(c: types.CallbackQuery, state: FSMContext):
    await c.message.edit_text("📝 **ШАГ 1: РЕГИСТРАЦИЯ**\n\nПосле регистрации отправьте ID в чат.", 
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 ПЕРЕЙТИ НА ПЛАТФОРМУ", url="https://u3.shortink.io/cabinet/demo-quick-high-low?a=RLQDltKf13Zlrj")]]))
    await state.set_state(FSM.reg)

@dp.message(FSM.reg)
async def check_id(m: types.Message, state: FSMContext):
    await m.answer("✅ **Депозит подтвержден. Режим:**", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Автомат", callback_data="m:auto")], [InlineKeyboardButton(text="⚙️ Ручной", callback_data="m:man")]]))
    await state.set_state(FSM.mode)

@dp.callback_query(F.data == "m:auto")
async def auto(c: types.CallbackQuery):
    intervals = ["5 сек", "15 сек", "30 сек", "1 мин", "2 мин", "3 мин", "4 мин", "5 мин"]
    expirations = ["2 мин", "3 мин", "4 мин", "5 мин"]
    text, kb = await get_signal_text(random.choice(LIVE), random.choice(intervals), random.choice(expirations))
    await c.message.edit_text(text, reply_markup=kb)

@dp.callback_query(F.data == "m:man")
async def man(c: types.CallbackQuery, state: FSMContext):
    await c.message.edit_text("🌍 Выберите рынок:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌍 Живой", callback_data="market:live")], [InlineKeyboardButton(text="💎 OTC", callback_data="market:otc")]]))
    await state.set_state(FSM.market)

@dp.callback_query(F.data.startswith("market:"))
async def market_choice(c: types.CallbackQuery, state: FSMContext):
    if c.data.split(":")[1] == "live":
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=p, callback_data=f"a:{p}")] for p in LIVE])
        await c.message.edit_text("🔹 Выберите актив:", reply_markup=kb)
        await state.set_state(FSM.asset)
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💵 Валюта", callback_data="cat:val")],
            [InlineKeyboardButton(text="🪙 Крипта", callback_data="cat:crypto")],
            [InlineKeyboardButton(text="📊 Акции", callback_data="cat:stock")]
        ])
        await c.message.edit_text("📂 Категория OTC:", reply_markup=kb)
        await state.set_state(FSM.cat)

@dp.callback_query(F.data.startswith("cat:"))
async def cat_choice(c: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=a, callback_data=f"a:{a}")] for a in OTC_DATA[c.data.split(":")[1]]])
    await c.message.edit_text("🔹 Выберите актив:", reply_markup=kb)
    await state.set_state(FSM.asset)

@dp.callback_query(F.data.startswith("a:"))
async def tf_choice(c: types.CallbackQuery, state: FSMContext):
    await state.update_data(asset=c.data.split(":")[1])
    intervals = ["5 сек", "15 сек", "30 сек", "1 мин", "2 мин", "3 мин", "4 мин", "5 мин"]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=i, callback_data=f"tf:{i}")] for i in intervals])
    await c.message.edit_text("⏳ Интервал свечи:", reply_markup=kb)
    await state.set_state(FSM.tf)

@dp.callback_query(F.data.startswith("tf:"))
async def exp_choice(c: types.CallbackQuery, state: FSMContext):
    await state.update_data(tf=c.data.split(":")[1])
    expirations = ["2 мин", "3 мин", "4 мин", "5 мин"]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=e, callback_data=f"exp:{e}")] for e in expirations])
    await c.message.edit_text("⌛️ Экспирация:", reply_markup=kb)
    await state.set_state(FSM.exp)

@dp.callback_query(F.data.startswith("exp:"))
async def final(c: types.CallbackQuery, state: FSMContext):
    d = await state.get_data()
    text, kb = await get_signal_text(d['asset'], d['tf'], c.data.split(":")[1])
    await c.message.edit_text(text, reply_markup=kb)

# --- ЗАПУСК ---
async def run_app():
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="Bot is running"))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080))).start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(run_app())
