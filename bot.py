import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Настройки
API_TOKEN = '8637835333:AAE5Y70U3VzEPdAmPCM3kmAxbKI8DDfbFx4'
ADMIN_ID = 6765689893
REF_LINK = "https://pocket-friends.co/r/vmbewy0x1o"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# База статусов
user_db = {} 

# Полный список активов
assets = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "USD/CHF", "NZD/USD",
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT",
    "AAPL (Apple)", "TSLA (Tesla)", "NVDA (NVIDIA)", "AMZN (Amazon)", "MSFT (Microsoft)",
    "GOOGL (Alphabet)", "META (Meta)", "AMD (AMD)", "NFLX (Netflix)"
]

def get_signal_message():
    asset = random.choice(assets)
    return (f"📡 **СИГНАЛ**\n\n"
            f"🔹 **Актив:** {asset}\n"
            f"⚡️ **Направление:** {random.choice(['📈 BUY', '📉 SELL'])}\n"
            f"⏱ **Время:** {random.randint(1, 5)} мин\n"
            f"🔥 **Точность:** {random.randint(85, 99)}%")

@dp.message(Command("start"))
async def start(message: types.Message):
    photo_url = "https://img.freepik.com/free-vector/robot-character-holding-tablet_23-2148218151.jpg"
    text = (
        "🤖 **Привет! Я — твой AI-помощник для торговли.**\n\n"
        "Я сканирую рынок 24/7. Для начала работы пройди регистрацию:"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Регистрация", url=REF_LINK)],
        [InlineKeyboardButton(text="✅ Зарегистрировался", callback_data="registered")]
    ])
    await bot.send_photo(chat_id=message.chat.id, photo=photo_url, caption=text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "registered")
async def process_reg(call: types.CallbackQuery):
    await call.message.answer("Пришли мне свой ID с платформы (просто напиши цифры).")
    user_db[call.from_user.id] = 'pending_id'

@dp.message(F.text.isdigit())
async def get_id(message: types.Message):
    if user_db.get(message.from_user.id) == 'pending_id':
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ ПРИНЯТЬ", callback_data=f"app_id_{message.from_user.id}")],
            [InlineKeyboardButton(text="❌ ОТКАЗАТЬ", callback_data=f"rej_id_{message.from_user.id}")]
        ])
        await bot.send_message(ADMIN_ID, f"ID пользователя {message.from_user.id}: {message.text}", reply_markup=kb)
        await message.answer("ID отправлен на проверку админу.")

@dp.callback_query(F.data.startswith("app_id_"))
async def approve_id(call: types.CallbackQuery):
    uid = int(call.data.split("_")[2])
    user_db[uid] = 'registered'
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💳 Я ПОПОЛНИЛ ($20+)", callback_data="paid")]])
    await bot.send_message(uid, "ID принят! Теперь пополни счет от $20 и нажми кнопку:", reply_markup=kb)
    await call.message.edit_text("ID одобрен.")

@dp.callback_query(F.data == "paid")
async def check_pay(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ ДОПУСТИТЬ", callback_data=f"app_pay_{call.from_user.id}")],
        [InlineKeyboardButton(text="❌ ОТКАЗАТЬ", callback_data=f"rej_pay_{call.from_user.id}")]
    ])
    await bot.send_message(ADMIN_ID, f"Юзер {call.from_user.id} нажал 'Я пополнил'. Проверь баланс!", reply_markup=kb)
    await call.message.answer("Запрос на проверку пополнения отправлен.")

@dp.callback_query(F.data.startswith("app_pay_"))
async def approve_pay(call: types.CallbackQuery):
    uid = int(call.data.split("_")[2])
    user_db[uid] = 'paid'
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔥 ПОЛУЧИТЬ СИГНАЛ", callback_data="get_signal")]])
    await bot.send_message(uid, "✅ Пополнение подтверждено! Доступ к сигналам открыт.", reply_markup=kb)
    await call.message.edit_text("Пополнение одобрено.")

@dp.callback_query(F.data == "get_signal")
async def send_sig(call: types.CallbackQuery):
    if user_db.get(call.from_user.id) == 'paid':
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔥 ЕЩЕ СИГНАЛ", callback_data="get_signal")]])
        await call.message.answer(get_signal_message(), reply_markup=kb, parse_mode="Markdown")
    else:
        await call.answer("Сначала пополни счет от $20!")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
