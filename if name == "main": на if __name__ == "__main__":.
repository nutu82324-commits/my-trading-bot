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

# Базы данных:
# authorized_users - те, кому можно давать сигналы
# pending_approvals - те, кто ждет подтверждения админа
authorized_users = set()
pending_approvals = {}

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
    conf = random.randint(75, 99) 
    end_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
    
    return (f"📡 СИГНАЛ\n\n🔹 Активы: {asset}\n⚡️ Направление: {direction}\n"
            f"⏱ Время: {minutes} мин\n⏳ Закрыть в: {end_time.strftime('%H:%M:%S')}\n"
            f"🔥 Уверенность: {conf}%\n\n✅ ВХОД: В первые 5-10 сек.")

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Регистрация", url=REF_LINK)],
        [InlineKeyboardButton(text="✅ Я зарегистрировался", callback_data="i_registered")]
    ])
    await message.answer("Привет! Зарегистрируйся по ссылке и нажми кнопку:", reply_markup=kb)

@dp.callback_query(F.data == "i_registered")
async def ask_id(call: types.CallbackQuery):
    await call.message.answer("Пришлите ваш ID (любое число), чтобы я передал его администратору.")
    pending_approvals[call.from_user.id] = "waiting_id"

@dp.message(F.text.regexp(r'\d+'))
async def process_id(message: types.Message):
    if pending_approvals.get(message.from_user.id) == "waiting_id":
        user_id_text = message.text
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{message.from_user.id}")],
            [InlineKeyboardButton(text="❌ Отказать", callback_data=f"deny_{message.from_user.id}")]
        ])
        await bot.send_message(ADMIN_ID, f"Заявка от {message.from_user.full_name} (ID: {user_id_text})", reply_markup=kb)
        await message.answer("Ваш ID отправлен админу. Ждите подтверждения.")
        pending_approvals[message.from_user.id] = "pending"

@dp.callback_query(F.data.startswith("accept_"))
async def accept_user(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    await bot.send_message(user_id, "Админ одобрил! Пополните баланс на $20 и нажмите кнопку.", 
                           reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                               [InlineKeyboardButton(text="💰 Я пополнил", callback_data="paid")]]))
    await call.message.edit_text("Пользователь принят.")

@dp.callback_query(F.data == "paid")
async def paid_button(call: types.CallbackQuery):
    await bot.send_message(ADMIN_ID, f"Пользователь {call.from_user.id} нажал 'Я пополнил'. Проверьте баланс!")
    await call.message.answer("Заявка на проверку пополнения отправлена админу.")
    # Добавляем в список разрешенных
    authorized_users.add(call.from_user.id)

@dp.message(Command("get"))
async def get_signal(message: types.Message):
    if message.from_user.id in authorized_users:
        await message.answer(get_signal_message())
    else:
        await message.answer("У вас нет доступа. Зарегистрируйтесь и пополните баланс (/start).")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
