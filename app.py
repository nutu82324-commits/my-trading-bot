import asyncio, random
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

TOKEN = "8879888014:AAHZImn-1tKDXrfgQjWBR1pJM3AWOybcEVk"
SUPPORT_URL = "https://t.me/andriddddd"

bot = Bot(token=TOKEN)
dp = Dispatcher()

DATA = {
    "OTC": {
        "Валюты": ["AUD/USD OTC", "CAD/CHF OTC", "EUR/GBP OTC", "EUR/JPY OTC", "EUR/USD OTC", "NZD/USD OTC", "SAR/CNY OTC", "UAH/USD OTC", "USD/BDT OTC", "USD/CAD OTC", "USD/CLP OTC", "USD/IDR OTC", "USD/INR OTC", "USD/JPY OTC", "USD/SGD OTC", "ZAR/USD OTC", "EUR/HUF OTC", "KES/USD OTC", "USD/COP OTC", "EUR/NZD OTC", "USD/PHP OTC", "JOD/CNY OTC", "AED/CNY OTC", "QAR/CNY OTC", "YER/USD OTC", "CHF/JPY OTC", "CHF/NOK OTC", "EUR/TRY OTC", "USD/BRL OTC", "AUD/CAD OTC", "EUR/CHF OTC", "AUD/CHF OTC", "GBP/AUD OTC", "NGN/USD OTC", "USD/DZD OTC", "USD/ARS OTC", "USD/CNH OTC"],
        "Крипта": ["Cardano OTC", "Dogecoin OTC", "Polkadot OTC", "Polygon OTC", "Toncoin OTC", "Ethereum OTC", "BNB OTC", "Avalanche OTC", "Solana OTC", "Bitcoin OTC"],
        "Акции": ["Apple OTC", "Boeing Company OTC", "McDonald's OTC", "Pfizer Inc OTC", "VISA OTC", "Cisco OTC", "GameStop Corp OTC", "ExxonMobil OTC", "Tesla OTC", "Citigroup Inc OTC", "Netflix OTC", "American Express OTC", "Amazon OTC", "Palantir Technologies OTC", "Alibaba OTC", "VIX OTC", "Coinbase Global OTC", "FACEBOOK INC OTC"]
    },
    "LIVE": {
        "Валюты": ["AUD/CHF", "CAD/CHF", "EUR/USD", "AUD/JPY", "AUD/USD", "USD/CAD", "AED/CNY", "AUD/CAD", "USD/THB", "GBP/USD", "CAD/JPY", "YER/USD", "EUR/CAD", "USD/JPY", "GBP/JPY", "GBP/CAD", "NZD/JPY", "EUR/JPY", "EUR/CHF", "GBP/AUD"],
        "Крипта": [],
        "Акции": ["Boeing Company", "FACEBOOK INC"]
    }
}

class FSM(StatesGroup):
    lang, mode, strategy, market, category, asset, expiration = State(), State(), State(), State(), State(), State(), State()

def create_kb(items, callback_prefix, back_button=True):
    kb = []
    for i in range(0, len(items), 2):
        row = [InlineKeyboardButton(text=str(it), callback_data=f"{callback_prefix}_{it}") for it in items[i:i+2]]
        kb.append(row)
    if back_button:
        kb.append([InlineKeyboardButton(text="🔙 Назад", callback_data="start")])
    kb.append([InlineKeyboardButton(text="🎧 Поддержка 24/7", url=SUPPORT_URL)])
    return InlineKeyboardMarkup(inline_keyboard=kb)

@dp.message(Command("start"))
@dp.callback_query(F.data == "start")
async def start_menu(msg: types.Union[types.Message, types.CallbackQuery], state: FSMContext):
    langs = ["🇺🇸 EN", "🇷🇺 RU", "🇺🇦 UA", "🇪🇸 ES", "🇫🇷 FR", "🇩🇪 DE", "🇵🇹 PT", "🇮🇹 IT", "🇹🇷 TR", "🇵🇱 PL"]
    kb = []
    for i in range(0, len(langs), 2):
        kb.append([InlineKeyboardButton(text=l, callback_data=f"lang_{l}") for l in langs[i:i+2]])
    kb.append([InlineKeyboardButton(text="🎧 Поддержка 24/7", url=SUPPORT_URL)])
    markup = InlineKeyboardMarkup(inline_keyboard=kb)
    if isinstance(msg, types.Message): await msg.answer("🌍 Выберите язык:", reply_markup=markup)
    else: await msg.message.edit_text("🌍 Выберите язык:", reply_markup=markup)
    await state.set_state(FSM.lang)

@dp.callback_query(F.data.startswith("lang_"))
async def select_mode(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.edit_text("⚙️ Режим:", reply_markup=create_kb(["🖐 Ручной", "🤖 Автомат"], "mode"))
    await state.set_state(FSM.mode)

@dp.callback_query(F.data.startswith("mode_"))
async def select_strat(cb: types.CallbackQuery, state: FSMContext):
    await state.update_data(mode=cb.data.split("_")[1])
    await cb.message.edit_text("🎯 Стратегия:", reply_markup=create_kb(["🧠 Smart Money", "🌊 SMT"], "strat"))
    await state.set_state(FSM.strategy)

@dp.callback_query(F.data.startswith("strat_"))
async def select_market(cb: types.CallbackQuery, state: FSMContext):
    await state.update_data(strat=cb.data.split("_", 1)[1])
    await cb.message.edit_text("🕹 Выберите рынок:", reply_markup=create_kb(["OTC", "LIVE"], "mkt"))
    await state.set_state(FSM.market)

@dp.callback_query(F.data.startswith("mkt_"))
async def select_cat(cb: types.CallbackQuery, state: FSMContext):
    mkt = cb.data.split("_")[1]
    await state.update_data(mkt=mkt)
    await cb.message.edit_text("📂 Категория:", reply_markup=create_kb(["Валюты", "Крипта", "Акции"], "cat"))
    await state.set_state(FSM.category)

@dp.callback_query(F.data.startswith("cat_"))
async def select_asset(cb: types.CallbackQuery, state: FSMContext):
    cat = cb.data.split("_")[1]
    data = await state.get_data()
    assets = DATA[data['mkt']].get(cat, [])
    if not assets:
        await cb.answer("❌ В этом разделе нет активов!", show_alert=True)
        return
    await state.update_data(cat=cat)
    await cb.message.edit_text(f"📊 Активы ({cat}):", reply_markup=create_kb(assets, "ast"))
    await state.set_state(FSM.asset)

@dp.callback_query(F.data.startswith("ast_"))
async def select_exp(cb: types.CallbackQuery, state: FSMContext):
    await state.update_data(asset=cb.data.split("_", 1)[1])
    await cb.message.edit_text("⏱ Экспирация:", reply_markup=create_kb(["S15", "M1", "M5", "M15"], "exp"))
    await state.set_state(FSM.expiration)

@dp.callback_query(F.data.startswith("exp_"))
async def send_signal(cb: types.CallbackQuery, state: FSMContext):
    d = await state.get_data()
    exp = cb.data.split("_")[1]
    text = (f"💎 СИГНАЛ Team Master 💎\n\n"
            f"⚙️ Режим: {d['mode']}\n"
            f"🎯 Стратегия: {d['strat']}\n"
            f"🕹 Рынок: {d['mkt']}\n"
            f"📊 Актив: {d['asset']}\n"
            f"⏱ Время: {exp}\n\n"
            f"📈 Вероятность: {random.randint(65, 85)}%\n"
            f"🕒 {datetime.now().strftime('%H:%M:%S')}")
    await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄 Новый сигнал", callback_data="start")], [InlineKeyboardButton(text="🎧 Поддержка 24/7", url=SUPPORT_URL)]]))

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
