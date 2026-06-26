import asyncio
import random
import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

# --- НАСТРОЙКИ ---
logging.basicConfig(level=logging.INFO)
BOT_TOKEN = "8643698714:AAF0ucnrgpNHzlD1G6dD7FZXVk5Jm6jpxUM"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- РАСШИРЕННАЯ БАЗА АКТИВОВ ---
LIVE = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CAD", "USD/CHF", "AUD/USD", "NZD/USD", "EUR/JPY", "GBP/JPY", "AUD/CAD", "EUR/AUD", "EUR/CAD", "CAD/CHF", "GBP/AUD", "NZD/JPY"]
OTC_GROUPS = {
    "val": ["AED/CNY OTC", "BHD/CNY OTC", "EUR/GBP OTC", "EUR/TRY OTC", "GBP/JPY OTC", "MAD/USD OTC", "NGN/USD OTC", "NZD/USD OTC", "USD/CNH OTC", "USD/EGP OTC", "USD/PHP OTC", "USD/PKR OTC", "USD/SGD OTC", "USD/THB OTC", "USD/VND OTC"],
    "crypto": ["Bitcoin OTC", "Ethereum OTC", "BNB OTC", "Solana OTC", "Cardano OTC", "Ripple OTC", "Dogecoin OTC", "Polkadot OTC", "Litecoin OTC"],
    "stock": ["Tesla OTC", "Apple OTC", "Facebook OTC", "Amazon OTC", "Google OTC", "Netflix OTC", "Nvidia OTC", "Microsoft OTC"]
}

class FSM(StatesGroup):
    registration = State()
    mode_selection = State()
    market_selection = State()
    category_selection = State()
    asset_selection = State()
    timeframe_selection = State()
    expiration_selection = State()

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def generate_signal_ui(asset, tf, exp):
    directions = [("🟢 BUY / ВВЕРХ", "📈"), ("🔴 SELL / ВНИЗ", "📉")]
    dir_text, dir_icon = random.choice(directions)
    
    text = (
        f"📡 **СИГНАЛ TEAM MASTER: QUANTUM CORE**\n\n"
        f"🔷 **Актив:** `{asset}`\n"
        f"⚡️ **Направление:** {dir_icon} {dir_text}\n"
        f"📊 **ТФ:** `{tf}`\n"
        f"⏱ **Экспирация:** `{exp}`\n"
        f"⏳ **Вход до:** {(asyncio.get_event_loop().time() + 300):.0f}\n"
        f"🎯 **Выплата:** `{random.randint(90, 96)}%`\n"
        f"🔥 **Индекс уверенности:** `{random.randint(93, 98)}%`\n\n"
        "⚠️ *Соблюдайте правила управления капиталом.*"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Сгенерировать новый", callback_data="m:auto")],
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_menu")]
    ])
    return text, kb

# --- ХЕНДЛЕРЫ ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 RU", callback_data="lang:ru"), InlineKeyboardButton(text="🇺🇸 EN", callback_data="lang:en")],
        [InlineKeyboardButton(text="🇺🇦 UA", callback_data="lang:ua"), InlineKeyboardButton(text="🇩🇪 DE", callback_data="lang:de")]
    ])
    text = (
        "👑 **TEAM MASTER: QUANTUM CORE SYSTEM v4.5**\n\n"
        "Система инициализирована. Мы анализируем рыночные данные 24/7.\n\n"
        "🌐 **Выберите язык интерфейса:**"
    )
    await message.answer(text, reply_markup=kb)

@dp.callback_query(F.data.startswith("lang:"))
async def select_lang(callback: types.CallbackQuery, state: FSMContext):
    text = (
        "📝 **ШАГ 1: РЕГИСТРАЦИЯ В СИСТЕМЕ**\n\n"
        "Для активации торгового ядра пройдите регистрацию по ссылке ниже. "
        "После этого скопируйте ваш ID и пришлите его боту."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 ПЕРЕЙТИ НА ПЛАТФОРМУ", url="https://u3.shortink.io/cabinet/demo-quick-high-low?a=RLQDltKf13Zlrj")]
    ])
    await callback.message.edit_text(text, reply_markup=kb)
    await state.set_state(FSM.registration)

@dp.message(FSM.registration)
async def process_registration(message: types.Message, state: FSMContext):
    await message.answer(
        "✅ **ID принят. Активация прошла успешно!**\nВыберите режим работы:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🤖 Автоматический режим", callback_data="m:auto")],
            [InlineKeyboardButton(text="⚙️ Ручной режим", callback_data="m:man")]
        ])
    )
    await state.set_state(FSM.mode_selection)

@dp.callback_query(F.data == "m:auto")
async def auto_mode(callback: types.CallbackQuery):
    tf_list = ["5 сек", "15 сек", "30 сек", "1 мин", "2 мин", "3 мин", "4 мин", "5 мин"]
    exp_list = ["2 мин", "3 мин", "4 мин", "5 мин"]
    text, kb = generate_signal_ui(random.choice(LIVE), random.choice(tf_list), random.choice(exp_list))
    await callback.message.edit_text(text, reply_markup=kb)

@dp.callback_query(F.data == "m:man")
async def manual_mode(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🌍 **Выберите рынок для анализа:**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌍 Живой рынок", callback_data="market:live")],
            [InlineKeyboardButton(text="💎 OTC рынок", callback_data="market:otc")]
        ])
    )
    await state.set_state(FSM.market_selection)

@dp.callback_query(F.data.startswith("market:"))
async def market_selected(callback: types.CallbackQuery, state: FSMContext):
    if "live" in callback.data:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=asset, callback_data=f"a:{asset}")] for asset in LIVE])
        await callback.message.edit_text("🔹 **Выберите актив:**", reply_markup=kb)
        await state.set_state(FSM.asset_selection)
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💵 Валюты", callback_data="cat:val")],
            [InlineKeyboardButton(text="🪙 Крипта", callback_data="cat:crypto")],
            [InlineKeyboardButton(text="📊 Акции", callback_data="cat:stock")]
        ])
        await callback.message.edit_text("📂 **Выберите категорию OTC:**", reply_markup=kb)
        await state.set_state(FSM.category_selection)

@dp.callback_query(F.data.startswith("cat:"))
async def category_selected(callback: types.CallbackQuery, state: FSMContext):
    cat = callback.data.split(":")[1]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=a, callback_data=f"a:{a}")] for a in OTC_GROUPS[cat]])
    await callback.message.edit_text("🔹 **Выберите актив:**", reply_markup=kb)
    await state.set_state(FSM.asset_selection)

@dp.callback_query(F.data.startswith("a:"))
async def asset_selected(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(asset=callback.data.split(":")[1])
    tfs = ["5 сек", "15 сек", "30 сек", "1 мин", "2 мин", "3 мин", "4 мин", "5 мин"]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=f"tf:{t}")] for t in tfs])
    await callback.message.edit_text("⏳ **Выберите интервал свечи:**", reply_markup=kb)
    await state.set_state(FSM.timeframe_selection)

@dp.callback_query(F.data.startswith("tf:"))
async def tf_selected(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(tf=callback.data.split(":")[1])
    exps = ["2 мин", "3 мин", "4 мин", "5 мин"]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=e, callback_data=f"exp:{e}")] for e in exps])
    await callback.message.edit_text("⌛️ **Выберите экспирацию:**", reply_markup=kb)
    await state.set_state(FSM.expiration_selection)

@dp.callback_query(F.data.startswith("exp:"))
async def show_final_signal(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text, kb = generate_signal_ui(data['asset'], data['tf'], callback.data.split(":")[1])
    await callback.message.edit_text(text, reply_markup=kb)

# --- ЗАПУСК ---
async def on_startup():
    print("Bot is started and running...")

if __name__ == "__main__":
    # Запуск бота с веб-сервером для Render
    async def run_bot():
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="Bot is running!"))
    web.run_app(app, port=int(os.environ.get("PORT", 8080)))
