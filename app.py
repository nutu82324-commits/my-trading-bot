 import asyncio
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# --- КОНФИГУРАЦИЯ ---
BOT_TOKEN = "8643698714:AAEh3AdcOKgdhE5NJ4s7ebIAnsM6zGXdkLI"
WHITE_LIST = [6765689893, 8273386412]
SUPPORT_URL = "https://t.me/andriddddd"
PLATFORM_URL = "https://u3.shortink.io/cabinet/demo-quick-high-low?utm_campaign=850173&utm_source=affiliate&utm_medium=sr&a=RLQDltKf13Zlrj&al=1771346&ac=smart-link&cid=960963&code=WELCOME50"

# --- БАЗЫ АКТИВОВ ---
CURRENCIES = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CAD", "USD/CHF", "AUD/USD", "NZD/USD"]
CROSS_PAIRS = ["EUR/JPY", "GBP/JPY", "AUD/CAD", "EUR/AUD", "EUR/CAD", "CAD/CHF"]
OTC = ["AED/CNY OTC", "BHD/CNY OTC", "EUR/GBP OTC", "EUR/TRY OTC", "GBP/JPY OTC", "MAD/USD OTC", "NGN/USD OTC", "NZD/USD OTC", "USD/CNH OTC", "USD/EGP OTC", "USD/PHP OTC", "USD/PKR OTC", "USD/SGD OTC", "USD/THB OTC", "USD/VND OTC", "YER/USD OTC", "ZAR/USD OTC", "USD/CHF OTC", "USD/DZD OTC", "Cardano OTC", "Bitcoin ETF OTC", "BNB OTC", "Polkadot OTC", "Litecoin OTC", "Polygon OTC", "Solana OTC", "TRON OTC", "Chainlink OTC", "Bitcoin OTC", "American Express OTC", "FACEBOOK INC OTC", "Intel OTC", "VISA OTC", "Apple OTC", "Pfizer Inc OTC", "Cisco OTC", "Tesla OTC", "Alibaba OTC", "Palantir Technologies OTC"]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class SignalStates(StatesGroup):
    choosing_cat = State()
    choosing_asset = State()
    choosing_exp = State()

# --- КЛАВИАТУРЫ ---
def lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 RU", callback_data="lang:ru"), InlineKeyboardButton(text="🇺🇸 EN", callback_data="lang:en")],
        [InlineKeyboardButton(text="🇺🇦 UA", callback_data="lang:ua"), InlineKeyboardButton(text="🇩🇪 DE", callback_data="lang:de")],
        [InlineKeyboardButton(text="🇪🇸 ES", callback_data="lang:es"), InlineKeyboardButton(text="🇫🇷 FR", callback_data="lang:fr")]
    ])

def register_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 ПЕРЕЙТИ НА ПЛАТФОРМУ", url=PLATFORM_URL)]])

def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 АВТОМАТИЧЕСКИЙ РЕЖИМ", callback_data="auto")],
        [InlineKeyboardButton(text="⚙️ РУЧНОЙ РЕЖИМ", callback_data="manual")]
    ])

def signal_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 ПЕРЕКРЫТИЕ", callback_data="auto")],
        [InlineKeyboardButton(text="👨‍💻 ПОДДЕРЖКА", url=SUPPORT_URL)]
    ])

# --- ЛОГИКА ---
@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("👑 **TEAM MASTER: QUANTUM CORE SYSTEM v4.5**\n\nСистема инициализирована. Мы анализируем рыночные данные 24/7 для поиска оптимальных точек входа.\n\n🌐 **Выберите язык:**", reply_markup=lang_kb())

@dp.callback_query(F.data.startswith("lang:"))
async def registration_step(c: types.CallbackQuery):
    await c.message.answer("📝 **ШАГ 1: РЕГИСТРАЦИЯ В СИСТЕМЕ**\n\nДля обеспечения синхронизации вашего торгового аккаунта с нашим квантовым ядром, пройдите регистрацию и отправьте ID в этот чат.", reply_markup=register_kb())

@dp.message(F.text.isdigit())
async def auth(m: types.Message):
    if int(m.text) in WHITE_LIST:
        await m.answer("✅ **Синхронизация успешна!**", reply_markup=main_kb())
    else:
        await m.answer("❌ **Ошибка: ID не найден в базе данных квантового ядра.**")

# АВТО РЕЖИМ
@dp.callback_query(F.data == "auto")
async def auto_mode(c: types.CallbackQuery):
    asset = random.choice(CURRENCIES + CROSS_PAIRS + OTC)
    exp = random.randint(2, 5)
    sig = (f"🚀 **AI QUANTUM AUTO-SIGNAL**\n\n🔹 Актив: `{asset}`\n⏱ Экспирация: `{exp} мин`\n📈 Направление: 🟢 BUY / ВВЕРХ\n🎯 Индекс AI: `99.2%`")
    await c.message.answer(sig, reply_markup=signal_kb())

# РУЧНОЙ РЕЖИМ
@dp.callback_query(F.data == "manual")
async def manual_mode(c: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 Валюты", callback_data="cat:curr")],
        [InlineKeyboardButton(text="💱 Кросс-курсы", callback_data="cat:cross")],
        [InlineKeyboardButton(text="💎 OTC/Акции", callback_data="cat:otc")]
    ])
    await c.message.edit_text("📂 Выберите категорию:", reply_markup=kb)
    await state.set_state(SignalStates.choosing_cat)

@dp.callback_query(SignalStates.choosing_cat, F.data.startswith("cat:"))
async def select_asset(c: types.CallbackQuery, state: FSMContext):
    cat = c.data.split(":")[1]
    items = CURRENCIES if cat == "curr" else (CROSS_PAIRS if cat == "cross" else OTC)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=i, callback_data=f"asset:{i}")] for i in items[:8]])
    await c.message.edit_text("🔹 Выберите актив:", reply_markup=kb)
    await state.set_state(SignalStates.choosing_asset)

@dp.callback_query(SignalStates.choosing_asset, F.data.startswith("asset:"))
async def select_exp(c: types.CallbackQuery, state: FSMContext):
    asset = c.data.split(":")[1]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{i} мин", callback_data=f"exp:{asset}:{i}")] for i in [2, 3, 4, 5]])
    await c.message.edit_text("⏳ Экспирация:", reply_markup=kb)
    await state.set_state(SignalStates.choosing_exp)

@dp.callback_query(SignalStates.choosing_exp, F.data.startswith("exp:"))
async def final_signal(c: types.CallbackQuery, state: FSMContext):
    _, asset, exp = c.data.split(":")
    finish = (datetime.now() + timedelta(minutes=int(exp))).strftime("%H:%M:%S")
    sig = (f"📡 **СИГНАЛ TEAM MASTER**\n\n🔹 **Актив:** `{asset}`\n⚡️ **Направление:** 🟢 BUY\n⏱ **Экспирация:** `{exp} мин`\n⏳ **Вход до:** `{finish}`\n🔥 **Индекс:** `95%`")
    await c.message.answer(sig, reply_markup=signal_kb())
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
