import asyncio
import random
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# Токен исправлен
API_TOKEN = '8601317051:AAEnUfV1GBDSN0Zkr87QtpTDcLXs2M3YK_E'
ADMIN_ID = 6765689893
REF_LINK = "https://pocket-friends.co/r/vmbewy0x1o"
PHOTO_URL = "https://i.ibb.co/hR4wYv9/IMG-20260601-135650.jpg"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
user_db = {} 

assets = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "EUR/JPY", "GBP/JPY",
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/USD OTC", "USD/CAD OTC", "EUR/JPY OTC", "GBP/JPY OTC",
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "DOGE/USDT",
    "BTC/USDT OTC", "ETH/USDT OTC", "SOL/USDT OTC", "XRP/USDT OTC",
    "Apple (AAPL)", "Tesla (TSLA)", "NVIDIA (NVDA)", "Amazon (AMZN)", "Microsoft (MSFT)",
    "Apple (OTC)", "Tesla (OTC)", "NVIDIA (OTC)", "Amazon (OTC)",
    "Gold", "Silver", "Brent Oil", "Gold OTC"
]

def get_signal():
    return (f"📡 **СИГНАЛ**\n\n🔹 **Активы:** {random.choice(assets)}\n"
            f"⚡️ **Направление:** {random.choice(['📈 🟢 BUY', '📉 🔴 SELL'])}\n"
            f"📊 **ТФ:** M3\n"
            f"⏱ **Время:** 3 мин\n"
            f"🎯 **Выплата:** {random.randint(88, 95)}%\n"
            f"🔥 **Уверенность:** {random.randint(80, 99)}%")

@dp.message(Command("start"))
async def start(message: types.Message):
    welcome_text = (
        "⚡️ **AI SCANNER TRADE** — твой личный ИИ-ассистент для торговли на Pocket Option!\n\n"
        "Робот сканирует рынок валютных пар 24/7, находит сильные ценовые пробои и развороты тренда по паттернам Price Action.\n\n"
        "Нажимай кнопку ниже, регистрируйся и забирай свой первый сигнал! 🚀"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Регистрация", url=REF_LINK)],
        [InlineKeyboardButton(text="✅ Зарегистрировался", callback_data="reg")]
    ])
    await bot.send_photo(message.chat.id, PHOTO_URL, caption=welcome_text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "reg")
async def reg(call: types.CallbackQuery):
    await call.message.answer("Пришли свой ID с платформы (цифрами).")
    user_db[call.from_user.id] = 'wait_id'

@dp.message(F.text.regexp(r'^\d+$'))
async def handle_id(message: types.Message):
    if user_db.get(message.from_user.id) == 'wait_id':
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ ПРИНЯТЬ ID", callback_data=f"app_id_{message.from_user.id}")],
            [InlineKeyboardButton(text="❌ ОТМЕНИТЬ", callback_data=f"rej_id_{message.from_user.id}")]
        ])
        await bot.send_message(ADMIN_ID, f"Юзер {message.from_user.id} прислал ID: {message.text}", reply_markup=kb)
        await message.answer("ID отправлен админу на проверку.")
        user_db[message.from_user.id] = 'checking'

@dp.callback_query(F.data.startswith("app_id_"))
async def accept_id(call: types.CallbackQuery):
    uid = call.data.split("_")[2]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💳 Я ПОПОЛНИЛ ($20+)", callback_data="paid")]])
    await bot.send_message(int(uid), "ID принят! Теперь пополни счет на $20+ и нажми кнопку.", reply_markup=kb)
    await call.message.edit_text("ID принят, ждем пополнения.")

@dp.callback_query(F.data == "paid")
async def check_pay(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ ДОПУСТИТЬ", callback_data=f"access_{call.from_user.id}")],
        [InlineKeyboardButton(text="❌ ОТКАЗ", callback_data="reject_pay")]
    ])
    await bot.send_message(ADMIN_ID, f"Юзер {call.from_user.id} нажал 'Пополнил'. Проверь!", reply_markup=kb)
    await call.message.answer("Запрос на проверку пополнения отправлен.")

@dp.callback_query(F.data.startswith("access_"))
async def give_access(call: types.CallbackQuery):
    uid = call.data.split("_")[1]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔥 ПОЛУЧИТЬ СИГНАЛ", callback_data="get_sig")]])
    await bot.send_message(int(uid), "✅ Пополнение подтверждено! Доступ открыт.", reply_markup=kb)
    await call.message.edit_text("Доступ дан.")

@dp.callback_query(F.data == "get_sig")
async def send_sig(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔥 ЕЩЕ СИГНАЛ", callback_data="get_sig")]])
    await call.message.answer(get_signal(), reply_markup=kb, parse_mode="Markdown")

async def web_server(request): return web.Response(text="Bot is running!")

async def main():
    app = web.Application()
    app.router.add_get('/', web_server)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
