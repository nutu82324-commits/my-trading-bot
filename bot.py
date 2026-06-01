import asyncio
import random
import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8637835333:AAE5Y70U3VzEPdAmPCM3kmAxbKI8DDfbFx4'
REF_LINK = "https://pocket-friends.co/r/vmbewy0x1o"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
user_db = set() 

all_assets = [
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/USD OTC", 
    "USD/CAD OTC", "NZD/USD OTC", "EUR/JPY OTC", "GBP/JPY OTC", 
    "Bitcoin OTC", "Ethereum OTC", "Litecoin OTC", "Ripple OTC", 
    "Apple OTC", "Tesla OTC", "NVIDIA OTC", "Amazon OTC", 
    "Gold OTC", "Silver OTC", "Brent Crude Oil OTC", "Natural Gas OTC"
]

def get_signal_message():
    asset = random.choice(all_assets)
    direction = random.choice(["📈 🟢 BUY", "📉 🔴 SELL"])
    minutes = random.randint(1, 5) 
    tf = f"M{minutes}"
    conf = random.randint(75, 99) 
    end_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
    time_str = end_time.strftime("%H:%M:%S")
    
    advice = """✅ КАК ВХОДИТЬ:
1. ⏳ ВХОД: В первые 5-10 сек после сигнала.
2. Мани-менеджмент: 2-3% от баланса."""
    
    return (f"📡 СИГНАЛ\n\n"
            f"🔹 Активы: {asset}\n"
            f"⚡️ Направление: {direction}\n"
            f"📊 ТФ: {tf}\n"
            f"⏱ Время: {minutes} мин\n"
            f"⏳ Закрыть в: {time_str}\n"
            f"🔥 Уверенность: {conf}%\n\n"
            f"{advice}")

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Регистрация", url=REF_LINK)],
        [InlineKeyboardButton(text="✅ Получить доступ", callback_data="get_access")]
    ])
    await message.answer("Привет! Нажми кнопку для получения доступа:", reply_markup=kb)

@dp.callback_query(F.data == "get_access")
async def get_access(call: types.CallbackQuery):
    user_db.add(call.from_user.id)
    await call.answer("Доступ открыт!")
    await call.message.edit_text("✅ Доступ открыт! Используй команду /get для получения сигнала.")

@dp.message(Command("get"))
async def get_signal(message: types.Message):
    if message.from_user.id in user_db:
        await message.answer(get_signal_message())
    else:
        await message.answer("Сначала нажми кнопку в /start")

async def main():
    # Бот будет ждать сообщений бесконечно, пока Pydroid запущен
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
