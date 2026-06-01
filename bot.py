import asyncio
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Настройки
API_TOKEN = '8637835333:AAE5Y70U3VzEPdAmPCM3kmAxbKI8DDfbFx4'
ADMIN_ID = 6765689893
REF_LINK = "https://pocket-friends.co/r/vmbewy0x1o"
# Вставьте сюда прямую ссылку на вашу картинку IMG_20260601_135650_803.jpg
PHOTO_URL = "https://i.ibb.co/hR4wYv9/IMG-20260601-135650.jpg" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_db = {} 

# Полный список всех активов
assets = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "USD/CHF", "NZD/USD", "EUR/JPY", "GBP/JPY",
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/USD OTC", "USD/CAD OTC", "EUR/JPY OTC", "GBP/JPY OTC", "NZD/USD OTC",
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "DOGE/USDT", "ADA/USDT", "LTC/USDT", "DOT/USDT",
    "BTC/USDT OTC", "ETH/USDT OTC", "SOL/USDT OTC", "XRP/USDT OTC",
    "Apple (AAPL)", "Tesla (TSLA)", "NVIDIA (NVDA)", "Amazon (AMZN)", "Microsoft (MSFT)", "Alphabet (GOOGL)", "Meta (META)", "AMD (AMD)", "Netflix (NFLX)",
    "Apple (OTC)", "Tesla (OTC)", "NVIDIA (OTC)", "Amazon (OTC)",
    "Gold", "Silver", "Brent Oil", "Gold OTC"
]

def get_signal_message():
    asset = random.choice(assets)
    direction = random.choice(['📈 🟢 BUY', '📉 🔴 SELL'])
    expiry_time = (datetime.now() + timedelta(minutes=3)).strftime("%H:%M:%S")
    
    return (f"📡 **СИГНАЛ**\n\n"
            f"🔹 **Активы:** {asset}\n"
            f"⚡️ **Направление:** {direction}\n"
            f"📊 **ТФ:** M3\n"
            f"⏱ **Время:** 3 мин\n"
            f"⏳ **До:** {expiry_time}\n"
            f"🎯 **Выплата:** {random.randint(88, 95)}%\n"
            f"🔥 **Уверенность:** {random.randint(80, 99)}%\n\n"
            f"💡 **Вход:** Входить в сделку сразу при получении сигнала.\n"
            f"💰 **Риск:** Рекомендуемый объем: 2-3% от депозита.")

@dp.message(Command("start"))
async def start(message: types.Message):
    text = ("🤖 **Привет! Я — твой AI-помощник.**\nПройди регистрацию для доступа к сигналам:")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Регистрация", url=REF_LINK)],
        [InlineKeyboardButton(text="✅ Зарегистрировался", callback_data="registered")]
    ])
    await bot.send_photo(chat_id=message.chat.id, photo=PHOTO_URL, caption=text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "registered")
async def process_reg(call: types.CallbackQuery):
    await call.message.answer("Пришли свой ID с платформы (числом).")
    user_db[call.from_user.id] = 'pending_id'

@dp.message(F.text.isdigit())
async def get_id(message: types.Message):
    if user_db.get(message.from_user.id) == 'pending_id':
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ ПРИНЯТЬ", callback_data=f"app_id_{message.from_user.id}")],
            [InlineKeyboardButton(text="❌ ОТКАЗАТЬ", callback_data=f"rej_id_{message.from_user.id}")]
        ])
        await bot.send_message(ADMIN_ID, f"ID {message.from_user.id}: {message.text}", reply_markup=kb)
        await message.answer("ID отправлен админу.")

@dp.callback_query(F.data.startswith("app_id_"))
async def approve_id(call: types.CallbackQuery):
    uid = int(call.data.split("_")[2])
    user_db[uid] = 'registered'
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💳 Я ПОПОЛНИЛ ($20+)", callback_data="paid")]])
    await bot.send_message(uid, "ID принят! Пополни счет ($20+) и нажми кнопку:", reply_markup=kb)
    await call.message.edit_text("ID одобрен.")

@dp.callback_query(F.data == "paid")
async def check_pay(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ ДОПУСТИТЬ", callback_data=f"app_pay_{call.from_user.id}")],
        [InlineKeyboardButton(text="❌ ОТКАЗАТЬ", callback_data=f"rej_pay_{call.from_user.id}")]
    ])
    await bot.send_message(ADMIN_ID, f"Юзер {call.from_user.id} нажал 'Пополнил'. Проверь!", reply_markup=kb)
    await call.message.answer("Запрос на проверку отправлен.")

@dp.callback_query(F.data.startswith("app_pay_"))
async def approve_pay(call: types.CallbackQuery):
    uid = int(call.data.split("_")[2])
    user_db[uid] = 'paid'
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔥 ПОЛУЧИТЬ СИГНАЛ", callback_data="get_signal")]])
    await bot.send_message(uid, "✅ Пополнение подтверждено! Доступ открыт.", reply_markup=kb)
    await call.message.edit_text("Пополнение одобрено.")

@dp.callback_query(F.data == "get_signal")
async def send_sig(call: types.CallbackQuery):
    if user_db.get(call.from_user.id) == 'paid':
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔥 ЕЩЕ СИГНАЛ", callback_data="get_signal")]])
        await call.message.answer(get_signal_message(), reply_markup=kb, parse_mode="Markdown")
    else:
        await call.answer("Сначала пополни счет!")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
