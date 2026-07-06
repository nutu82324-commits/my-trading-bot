import hashlib
import aiohttp
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8479849828:AAEl31VYsy9o7NrSL9lIHdmHDaUBrbP1aFw"
ADMIN_ID = YOUR_ID_HERE  # Вставь свой ID, например: 123456789
PARTNER_ID = 'ВАШ_PARTNER_ID'
SECRET = 'Zc4X9zu0EMrqbPuLy3tN'

# Настройка логов для отслеживания ошибок
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher()

# Хранилище блокировок
blocked_users = set()

# --- ФУНКЦИИ БЕЗОПАСНОСТИ ---
def is_blocked(user_id: int):
    return user_id in blocked_users

# --- СТАРТОВАЯ ЛОГИКА ---
@dp.message(Command("start"))
async def start_command(message: types.Message):
    # Если юзер заблокирован — молчим или шлем уведомление
    if is_blocked(message.from_user.id):
        return

    # Список языков
    languages = {
        "ru": "🇷🇺 Русский", "en": "🇺🇸 English", "es": "🇪🇸 Español",
        "pt": "🇵🇹 Português", "fr": "🇫🇷 Français", "de": "🇩🇪 Deutsch",
        "it": "🇮🇹 Italiano", "tr": "🇹🇷 Türkçe", "hi": "🇮🇳 Hindi", "ar": "🇸🇦 العربية"
    }
    
    builder = InlineKeyboardBuilder()
    for code, name in languages.items():
        builder.button(text=name, callback_data=f"lang_{code}")
    builder.adjust(2) # Кнопки по 2 в ряд

    # Описание бота (ровно 7 строк)
    desc = (
        "🤖 **AI TRADING BOT**\n"
        "📈 Наш алгоритм основан на Smart Money.\n"
        "📊 Точность сигналов — 80% проходимости.\n"
        "⚙️ Анализ рынка 24/7 в реальном времени.\n"
        "🔒 Безопасность и стабильный профит.\n"
        "💼 Присоединяйся к команде Team Master.\n"
        "👇 Выбери язык для начала работы:"
    )
    
    # Отправка фото (убедись, что файл в папке проекта)
    try:
        photo = types.FSInputFile("bot_photo.jpg")
        await message.answer_photo(photo=photo, caption=desc, reply_markup=builder.as_markup())
    except:
        await message.answer(desc, reply_markup=builder.as_markup())
    
    # Удаление сообщения пользователя для чистоты чата
    await message.delete()
# --- СЕРЕДИНА: ЛОГИКА API И РЕГИСТРАЦИИ ---

# 1. Функция проверки пользователя через API
async def verify_user(user_id):
    hash_str = hashlib.md5(f"{user_id}:{PARTNER_ID}:{SECRET}".encode()).hexdigest()
    url = f"https://affiliate.pocketoption.com/api/user-info/{user_id}/{PARTNER_ID}/{hash_str}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                data = await response.json()
                # Проверка депозита >= 20$
                return data.get("deposit", 0) >= 20
        except Exception as e:
            logging.error(f"API Error: {e}")
            return False

# 2. Обработка выбора языка и начало регистрации
@dp.callback_query(F.data.startswith("lang_"))
async def registration_flow(callback: types.CallbackQuery):
    text = (
        "🔗 **РЕГИСТРАЦИЯ В КОМАНДЕ**\n\n"
        "1. Перейдите по ссылке: [ВАША_ССЫЛКА]\n"
        "2. При регистрации введите промокод: `WELCOME50`\n"
        "3. Пополните баланс на сумму от 20$ и выше.\n"
        "4. Нажмите кнопку ниже для подтверждения данных."
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить пополнение", callback_data="verify_dep")
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

# 3. Верификация и уведомление АДМИНА
@dp.callback_query(F.data == "verify_dep")
async def verify_deposit(callback: types.CallbackQuery):
    user = callback.from_user
    
    if await verify_user(user.id):
        # Кнопки для тебя (админа)
        kb_admin = InlineKeyboardBuilder()
        kb_admin.button(text="🚫 Заблокировать", callback_data=f"ban_{user.id}")
        kb_admin.button(text="✅ Разблокировать", callback_data=f"unban_{user.id}")
        
        # Уведомление тебе в личку
        await bot.send_message(
            ADMIN_ID, 
            f"👤 Новый юзер: @{user.username or 'NoNick'}\nID: `{user.id}`\nСтатус: Верифицирован!", 
            reply_markup=kb_admin.as_markup()
        )
        
        # Юзеру — доступ к режимам
        builder = InlineKeyboardBuilder()
        builder.button(text="🚀 Перейти к сигналам", callback_data="mode_menu")
        await callback.message.edit_text("✅ Вы успешно приняты в команду Team Master!", reply_markup=builder.as_markup())
    else:
        await callback.answer("❌ Пополнение не найдено или сумма меньше 20$!", show_alert=True)

# 4. Управление блокировками (админка)
@dp.callback_query(F.data.startswith(("ban_", "unban_")))
async def admin_control(callback: types.CallbackQuery):
    action, target_id = callback.data.split("_")
    target_id = int(target_id)
    
    if action == "ban":
        blocked_users.add(target_id)
        await callback.message.edit_text(f"🚫 Пользователь {target_id} заблокирован.")
    elif action == "unban":
        blocked_users.discard(target_id)
        await callback.message.edit_text(f"✅ Пользователь {target_id} разблокирован.")
# --- ФИНАЛ: ЛОГИКА СИГНАЛОВ И РЕЖИМОВ ---

# 1. Меню выбора режима
@dp.callback_query(F.data == "mode_menu")
async def mode_menu(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🤖 Автоматический", callback_data="auto_mode")
    builder.button(text="👨‍💻 Ручной", callback_data="manual_mode")
    builder.adjust(1)
    await callback.message.edit_text("⚙️ Выберите режим работы:", reply_markup=builder.as_markup())

# 2. Ручной режим (выбор актива, ТФ, экспирации)
@dp.callback_query(F.data == "manual_mode")
async def manual_mode(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="💵 Валюты (FX)", callback_data="m_fx")
    builder.button(text="🪙 Криптовалюта", callback_data="m_crypto")
    builder.button(text="🏢 Акции", callback_data="m_stocks")
    builder.button(text="🔙 Назад", callback_data="mode_menu")
    builder.adjust(1)
    await callback.message.edit_text("📊 Выберите рынок:", reply_markup=builder.as_markup())

# Выбор актива (заглушка для демонстрации логики)
@dp.callback_query(F.data.startswith("m_"))
async def choose_asset(callback: types.CallbackQuery):
    cat = callback.data.split("_")[1]
    # Здесь логика подгрузки активов из data.py
    await callback.message.edit_text(f"Выберите актив из категории {cat.upper()}:")

# 3. Выдача сигнала
@dp.callback_query(F.data.startswith("sig_"))
async def final_signal(callback: types.CallbackQuery):
    # Тут собираются данные: актив, ТФ, время
    text = (
        f"🚀 **СИГНАЛ**\n\n"
        f"📊 **Актив:** EUR/USD OTC\n"
        f"⏱ **ТФ:** M1 | ⏳ **Эксп:** 1 мин\n"
        f"🎯 **Направление:** BUY\n"
        f"💰 **Выплата:** 88%\n\n"
        f"💡 **Советы:**\n"
        f"1. Соблюдай мани-менеджмент 2%.\n"
        f"2. Не заходи в сделку против сильного импульса."
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Новый сигнал", callback_data="manual_mode")
    builder.button(text="🔙 Назад", callback_data="mode_menu")
    builder.row(types.InlineKeyboardButton(text="🎧 Поддержка @andriddddd", url="https://t.me/andriddddd"))
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

# 4. Автоматический режим (заглушка)
@dp.callback_query(F.data == "auto_mode")
async def auto_mode(callback: types.CallbackQuery):
    await callback.message.edit_text("🤖 Бот анализирует рынок и подбирает лучшие пары...")
    await asyncio.sleep(2)
    await final_signal(callback)

# --- ЗАПУСК ---
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
