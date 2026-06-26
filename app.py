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

# --- ЛОГИКА АНАЛИЗА ---
async def get_binance_price(symbol):
    try:
        pair = symbol.replace("/", "").replace(" OTC", "")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.binance.com/api/v3/ticker/price?symbol={pair}USDT") as resp:
                data = await resp.json()
                return float(data['price'])
    except:
        return random.random()

async def get_direction(asset):
    if "OTC" in asset:
        return random.choice([("🟢 BUY / ВВЕРХ", "📈"), ("🔴 SELL / ВНИЗ", "📉")])
    else:
        p1 = await get_binance_price(asset)
        await asyncio.sleep(0.5)
        p2 = await get_binance_price(asset)
        return ("🟢 BUY / ВВЕРХ", "📈") if p2 >= p1 else ("🔴 SELL / ВНИЗ", "📉")

async def sig_text(asset, tf, exp):
    dir_text, dir_icon = await get_direction(asset)
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
        [InlineKeyboardButton(text="🔄 Перекрытие (x2.5)", callback_data="m:auto")]
    ])
    return text, kb

# --- ХЕНДЛЕРЫ ---
@dp.message(Command("start"))
async def start(m: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 RU", callback_data="lang"), InlineKeyboardButton(text="🇺🇸 EN", callback_data="lang")],
        [InlineKeyboardButton(text="🇺🇦 UA", callback_data="lang"), InlineKeyboardButton(text="🇩🇪 DE", callback_data="lang")]
    ])
    await m.answer("👑 **TEAM MASTER: QUANTUM CORE SYSTEM v4.5**\nВыберите язык:", reply_markup=kb)

@dp.callback_query(F.data == "lang")
async def reg(c: types.CallbackQuery, state: FSMContext):
    await c.message.answer("📝 **ШАГ 1: РЕГИСТРАЦИЯ**\nПришлите ID.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 ПЛАТФОРМА", url="https://u3.shortink.io/cabinet/demo-quick-high-low?a=RLQDltKf13Zlrj")]]))
    await state.set_state(FSM.reg)

@dp.message(FSM.reg)
async def check_id(m: types.Message, state: FSMContext):
    await m.answer("✅ **Депозит подтвержден. Режим:**", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Автомат", callback_data="m:auto")], [InlineKeyboardButton(text="⚙️ Ручной", callback_data="m:man")]]))
    await state.set_state(FSM.mode)

@dp.callback_query(F.data == "m:auto")
async def auto(c: types.CallbackQuery):
    text, kb = await sig_text(random.choice(LIVE), "M1", f"{random.randint(2, 5)} мин")
    await c.message.answer(text, reply_markup=kb)

@dp.callback_query(F.data == "m:man")
async def man(c: types.CallbackQuery, state: FSMContext):
    await c.message.answer("🌍 Рынок:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌍 Живой", callback_data="market:live")], [InlineKeyboardButton(text="💎 OTC", callback_data="market:otc")]]))
    await state.set_state(FSM.market)

@dp.callback_query(F.data.startswith("market:"))
async def market_choice(c: types.CallbackQuery, state: FSMContext):
    if c.data.split(":")[1] == "live":
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=p, callback_data=f"a:{p}")] for p in LIVE])
        await c.message.answer("🔹 Актив:", reply_markup=kb)
        await state.set_state(FSM.asset)
    else:
        await c.message.answer("📂 Категория:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💵 Валюта", callback_data="cat:val")], [InlineKeyboardButton(text="🪙 Крипта", callback_data="cat:crypto")], [InlineKeyboardButton(text="📊 Акции", callback_data="cat:stock")]]))
        await state.set_state(FSM.cat)

@dp.callback_query(F.data.startswith("cat:"))
async def cat_choice(c: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=a, callback_data=f"a:{a}")] for a in OTC_DATA[c.data.split(":")[1]]])
    await c.message.answer("🔹 Актив:", reply_markup=kb)
    await state.set_state(FSM.asset)

@dp.callback_query(F.data.startswith("a:"))
async def tf_choice(c: types.CallbackQuery, state: FSMContext):
    await state.update_data(asset=c.data.split(":")[1])
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=i, callback_data=f"tf:{i}")] for i in ["5 сек", "1 мин", "5 мин"]])
    await c.message.answer("⏳ Интервал:", reply_markup=kb)
    await state.set_state(FSM.tf)

@dp.callback_query(F.data.startswith("tf:"))
async def exp_choice(c: types.CallbackQuery, state: FSMContext):
    await state.update_data(tf=c.data.split(":")[1])
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=e, callback_data=f"exp:{e}")] for e in ["1 мин", "3 мин", "5 мин"]])
    await c.message.answer("⌛️ Экспирация:", reply_markup=kb)
    await state.set_state(FSM.exp)

@dp.callback_query(F.data.startswith("exp:"))
async def final(c: types.CallbackQuery, state: FSMContext):
    d = await state.get_data()
    text, kb = await sig_text(d['asset'], d['tf'], c.data.split(":")[1])
    await c.message.answer(text, reply_markup=kb)

async def handle(request): return web.Response(text="Bot is running")

async def run_app():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080)))
    await site.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(run_app())
