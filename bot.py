import asyncio
import random
import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8637835333:AAE5Y70U3VzEPdAmPCM3kmAxbKI8DDfbFx4'
ADMIN_ID = 6765689893
REF_LINK = "https://pocket-friends.co/r/vmbewy0x1o"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
authorized_users = set()

# Полный список активов (валюты, акции, крипта, OTC)
all_assets = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "EUR/JPY", "GBP/JPY", "USD/CAD", "NZD/USD", "USD/CHF",
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/USD OTC", "EUR/JPY OTC", "GBP/JPY OTC", "USD/CAD OTC", "NZD/USD OTC", "USD/CHF OTC",
    "Bitcoin", "Ethereum", "Litecoin", "Ripple", "Solana", "Cardano", "Dogecoin", "Binance Coin",
    "Bitcoin OTC", "Ethereum OTC", "Litecoin OTC", "Ripple OTC", "Solana OTC", "Cardano OTC", "Dogecoin OTC", "Binance Coin OTC",
    "Apple", "Tesla", "NVIDIA", "Amazon", "Google", "Meta", "Netflix", "Microsoft",
    "Apple OTC", "Tesla OTC", "NVIDIA OTC", "Amazon OTC", "Google OTC", "Meta OTC", "Netflix OTC", "Microsoft OTC",
    "Gold", "Silver", "Brent Crude Oil", "Natural Gas", "Platinum",
    "Gold OTC", "Silver OTC", "Brent Crude Oil OTC", "Natural Gas OTC", "Platinum OTC"
]

def get_signal_message():
    asset = random.choice(all_assets)
    direction = random.choice(["📈 🟢 BUY", "📉 🔴 SELL"])
    minutes = random.randint(1, 5) 
    end_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
    return (f"📡 СИГНАЛ\n\n🔹 Активы: {asset}\n⚡️ Направление: {direction}\n"
            f"⏱ Время: {minutes} мин\n⏳ До: {end_time.strftime('%H:%M:%S')}\n"
            f"🔥 Точность: {random.randint(80, 99)}%")

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Регистрация", url=REF_LINK)],
        [InlineKeyboardButton(text="✅ Я пополнил", callback_data="paid")]
    ])
    await message.answer("Добро пожаловать! Зарегистрируйся и нажми кнопку после пополнения:", reply_markup=kb)

@dp.callback_query(F.data == "paid")
async def paid_button(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ ПРИНЯТЬ", callback_data=f"approve_{call.from_user.id}")],
        [InlineKeyboardButton(text="❌ ОТКАЗАТЬ", callback_data=f"reject_{call.from_user.id}")]
    ])
    await bot.send_message(ADMIN_ID, f"👤 {call.from_user.full_name}\n🆔 {call.from_user.id}", reply_markup=kb)
    await call.answer("Заявка отправлена.")

@dp.callback_query(F.data.startswith("approve_"))
async def approve(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    authorized_users.add(user_id)
    await bot.send_message(user_id, "✅ Доступ открыт! Пиши /get")
    await call.message.edit_text(call.message.text + "\n\n✅ ОДОБРЕНО")

@dp.callback_query(F.data.startswith("reject_"))
async def reject(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    await bot.send_message(user_id, "❌ Пополнение не подтверждено.")
    await call.message.edit_text(call.message.text + "\n\n❌ ОТКЛОНЕНО")

@dp.message(Command("get"))
async def get_signal(message: types.Message):
    if message.from_user.id in authorized_users:
        await message.answer(get_signal_message())
    else:
        await message.answer("❌ Доступ не подтвержден.")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
