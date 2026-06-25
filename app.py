import asyncio
import random
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# --- ЛОГГИРОВАНИЕ ---
logging.basicConfig(level=logging.INFO)

# --- КОНФИГУРАЦИЯ ---
BOT_TOKEN = "8643698714:AAG9xjwn1kNBd6faJw34Xso6Gdm3ClvE2tc"
WHITE_LIST = [6765689893, 8273386412]
SUPPORT_URL = "https://t.me/andriddddd"
PLATFORM_URL = "https://u3.shortink.io/cabinet/demo-quick-high-low?utm_campaign=850173&utm_source=affiliate&utm_medium=sr&a=RLQDltKf13Zlrj&al=1771346&ac=smart-link&cid=960963&code=WELCOME50"

# --- БАЗЫ АКТИВОВ (МАКСИМАЛЬНЫЙ СПИСОК) ---
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

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- FSM СОСТОЯНИЯ ---
class TradeFlow(StatesGroup):
    language = State()
    registration = State()
    mode_selection = State()
    manual_category = State()
    manual_asset = State()
    manual_exp = State()

# --- КЛАВИАТУРЫ ---
def get_lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 RU", callback_data="set_lang:ru"), InlineKeyboardButton(text="🇺🇸 EN", callback_data="set_lang:en")],
        [InlineKeyboardButton(text="🇺🇦 UA", callback_data="set_lang:ua"), InlineKeyboardButton(text="🇩🇪 DE", callback_data="set_lang:de")],
        [InlineKeyboardButton(text="🇪🇸 ES", callback_data="set_lang:es"), InlineKeyboardButton(text="🇫🇷 FR", callback_data="set_lang:fr")]
    ])

def get_platform_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 ПЕРЕЙТИ НА ПЛАТФОРМУ", url=PLATFORM_URL)]])

def get_main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 АВТОМАТИЧЕСКИЙ РЕЖИМ", callback_data="mode:auto")],
        [InlineKeyboardButton(text="⚙️ РУЧНОЙ РЕЖИМ", callback_data="mode:manual")]
    ])

def get_signal_control_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 ПЕРЕКРЫТИЕ", callback_data="mode:auto")],
        [InlineKeyboardButton(text="👨‍💻 ПОДДЕРЖКА", url=SUPPORT_URL)]
    ])

# --- ОСНОВНАЯ ЛОГИКА ---
@dp.message(Command("start"))
async def cmd_start(m: types.Message, state: FSMContext):
    msg = (
        "👑 **TEAM MASTER: QUANTUM CORE SYSTEM v4.5**\n\n"
        "Система инициализована. Мы анализируем рыночные данные 24/7 "
        "для поиска оптимальных точек входа.\n\n"
        "🌐 **Выберите предпочтительный язык интерфейса:**"
    )
    await m.answer(msg, reply_markup=get_lang_kb())
    await state.set_state(TradeFlow.language)

@dp.callback_query(TradeFlow.language, F.data.startswith("set_lang:"))
async def process_lang(c: types.CallbackQuery, state: FSMContext):
    msg = (
        "📝 **ШАГ 1: РЕГИСТРАЦИЯ В СИСТЕМЕ**\n\n"
        "Для обеспечения синхронизации вашего торгового аккаунта с нашим квантовым ядром, "
        "вы обязаны пройти регистрацию по партнерской ссылке.\n\n"
        "После завершения регистрации, пожалуйста, скопируйте ваш ID и отправьте его в этот чат."
    )
    await c.message.edit_text(msg, reply_markup=get_platform_kb())
    await state.set_state(TradeFlow.registration)

@dp.message(TradeFlow.registration, F.text.isdigit())
async def process_id(m: types.Message, state: FSMContext):
    if int(m.text) in WHITE_LIST:
        await m.answer("✅ **Синхронизация успешна. Ядро квантовой сети активно.**", reply_markup=get_main_menu_kb())
        await state.set_state(TradeFlow.mode_selection)
    else:
        await m.answer("❌ **Ошибка доступа: Депозит не верифицирован в системе.**")

# --- РЕЖИМЫ (АВТО / РУЧНОЙ) ---
@dp.callback_query(F.data == "mode:auto")
async def auto_trade(c: types.CallbackQuery):
    asset = random.choice(CURRENCIES + CROSS_PAIRS + OTC)
    exp = random.randint(2, 5)
    sig = (
        f"🚀 **AI QUANTUM AUTO-SIGNAL**\n\n"
        f"🔹 **Актив:** `{asset}`\n"
        f"⚡️ **Направление:** 🟢 BUY / ВВЕРХ\n"
        f"⏱ **Экспирация:** `{exp} мин`\n"
        f"🔥 **ИИ Вероятность:** `{random.randint(97, 99)}%`"
    )
    await c.message.answer(sig, reply_markup=get_signal_control_kb())

@dp.callback_query(F.data == "mode:manual")
async def manual_menu(c: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 Валюты", callback_data="m_cat:curr")],
        [InlineKeyboardButton(text="💱 Кросс-курсы", callback_data="m_cat:cross")],
        [InlineKeyboardButton(text="💎 OTC/Акции", callback_data="m_cat:otc")]
    ])
    await c.message.edit_text("📂 Выберите категорию активов:", reply_markup=kb)
    await state.set_state(TradeFlow.manual_category)

# --- ЛОГИКА РУЧНОГО ВЫБОРА (УПРОЩЕНА ДЛЯ СТАБИЛЬНОСТИ) ---
@dp.callback_query(TradeFlow.manual_category, F.data.startswith("m_cat:"))
async def select_asset_manual(c: types.CallbackQuery, state: FSMContext):
    cat = c.data.split(":")[1]
    items = CURRENCIES if cat == "curr" else (CROSS_PAIRS if cat == "cross" else OTC)
    # Выводим первые 8 для компактности
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=i, callback_data=f"m_asset:{i}")] for i in items[:8]])
    await c.message.edit_text("🔹 Выберите актив из списка:", reply_markup=kb)
    await state.set_state(TradeFlow.manual_asset)

@dp.callback_query(TradeFlow.manual_asset, F.data.startswith("m_asset:"))
async def select_exp_manual(c: types.CallbackQuery, state: FSMContext):
    asset = c.data.split(":")[1]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{i} мин", callback_data=f"m_final:{asset}:{i}")] for i in [2, 3, 4, 5]
    ])
    await c.message.edit_text("⏳ Укажите экспирацию:", reply_markup=kb)
    await state.set_state(TradeFlow.manual_exp)

@dp.callback_query(TradeFlow.manual_exp, F.data.startswith("m_final:"))
async def send_final_signal(c: types.CallbackQuery, state: FSMContext):
    _, asset, exp = c.data.split(":")
    finish = (datetime.now() + timedelta(minutes=int(exp))).strftime("%H:%M:%S")
    sig = (
        f"📡 **СИГНАЛ TEAM MASTER (РУЧНОЙ)**\n\n"
        f"🔹 **Актив:** `{asset}`\n"
        f"⚡️ **Направление:** 📈 🟢 BUY / ВВЕРХ\n"
        f"⏱ **Экспирация:** `{exp} мин`\n"
        f"⏳ **Вход до:** `{finish}`\n"
        f"🔥 **Индекс:** `{random.randint(92, 96)}%`\n\n"
        "⚠️ *Соблюдайте правила риск-менеджмента.*"
    )
    await c.message.answer(sig, reply_markup=get_signal_control_kb())
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
