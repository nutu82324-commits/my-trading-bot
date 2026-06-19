import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- КОНФИГ ---
API_TOKEN = "8274315061:AAHdhg9IuA2zDAWPKQu_Oo5BTXfYnDSLi-I"
ADMIN_ID = 6765689893
REF_LINK = "https://u3.shortink.io/cabinet/try-demo?utm_campaign=848948&utm_source=affiliate&utm_medium=sr&a=ZLSYeXT7yX3bDG&al=1768735&ac=smart-link&cid=959257&code=WELCOME50"
PROMO_CODE = "WELCOME50"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- КЛАВИАТУРЫ ---
def get_main_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📈 Получить Сигнал", callback_data="get_sig"),
        InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        InlineKeyboardButton("⚙️ Настройки ИИ", callback_data="settings"),
        InlineKeyboardButton("💎 VIP Статус", callback_data="vip"),
        InlineKeyboardButton("🆘 Поддержка", callback_data="support"),
        InlineKeyboardButton("📢 О боте", callback_data="about")
    )
    return kb

def get_reg_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Перейти к регистрации", url=REF_LINK))
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data="main_menu"))
    return kb

# --- ЛОГИКА ---
async def send_signal_card(message: types.Message):
    signal_text = (
        "🔥 **HROM QUANTUM SIGNAL** 🔥\n\n"
        "📊 **Активы:** GOLD OTC\n"
        "⚡️ **Направление:** UP 🟢\n"
        "⏱ **Время:** 3 минуты\n"
        "🎯 **Точка входа:** Текущая\n"
        "🔥 **Вероятность:** 94%\n\n"
        "⚠️ Для доступа к полному функционалу используйте промокод: `WELCOME50` при пополнении!"
    )
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Зайти на биржу", url=REF_LINK))
    kb.add(InlineKeyboardButton("🔙 В главное меню", callback_data="main_menu"))
    
    await message.edit_text(signal_text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data == "main_menu")
async def back_to_main(call: types.CallbackQuery):
    await call.message.edit_text("🚀 **HROM QUANTUM CORE** — выберите действие:", reply_markup=get_main_kb())

@dp.callback_query_handler(lambda c: c.data == "get_sig")
async def process_signal(call: types.CallbackQuery):
    # Теперь при запросе сигнала бот напоминает о промокоде
    await send_signal_card(call.message)

@dp.message_handler(commands=['start', 'admin'])
async def start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🛠 **АДМИН-ПАНЕЛЬ**") # Добавьте сюда get_admin_kb()
    else:
        await message.answer("🚀 **HROM QUANTUM CORE**\n\nИспользуй промокод `WELCOME50` при пополнении для бонуса!", 
                             reply_markup=get_main_kb(), parse_mode="Markdown")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
