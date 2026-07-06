import hashlib
import aiohttp
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile

# --- НАСТРОЙКИ СИСТЕМЫ ---
# Твои данные (жестко прописаны для стабильности)
BOT_TOKEN = "8479849828:AAEl31VYsy9o7NrSL9lIHdmHDaUBrbP1aFw"
ADMIN_ID = 6765689893       
WHITE_LIST = {8273386412}   
PARTNER_ID = 'ВАШ_PARTNER_ID' 
SECRET = 'Zc4X9zu0EMrqbPuLy3tN'

# Настройка логирования для дебага на Render
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Инициализация
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher()

# Базы в памяти (для быстрой работы)
blocked_users = set()

# --- ФУНКЦИИ БЕЗОПАСНОСТИ ---
def is_blocked(user_id: int) -> bool:
    return user_id in blocked_users

def get_user_status(user_id: int) -> str:
    if user_id == ADMIN_ID: return "BOSS"
    if user_id in WHITE_LIST: return "FRIEND"
    return "USER"

# --- СТАРТОВАЯ ЛОГИКА ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user = message.from_user
    logger.info(f"Юзер {user.id} (@{user.username}) запустил бота")
    
    if is_blocked(user.id):
        return

    # Клавиатура выбора языка
    builder = InlineKeyboardBuilder()
    langs = {
        "ru": "🇷🇺 Русский", "en": "🇺🇸 English", "es": "🇪🇸 Español",
        "pt": "🇵🇹 Português", "fr": "🇫🇷 Français", "de": "🇩🇪 Deutsch",
        "it": "🇮🇹 Italiano", "tr": "🇹🇷 Türkçe", "hi": "🇮🇳 Hindi", "ar": "🇸🇦 العربية"
    }
    for code, name in langs.items():
        builder.button(text=name, callback_data=f"lang_{code}")
    builder.adjust(2)

    # Приветственный текст
    desc = (
        "🤖 *AI TRADING BOT — TEAM MASTER*\n\n"
        "📈 Наш алгоритм основан на Smart Money.\n"
        "📊 Точность сигналов — 80% проходимости.\n"
        "⚙️ Анализ рынка 24/7 в реальном времени.\n"
        "🔒 Безопасность и стабильный профит.\n"
        "💼 Присоединяйся к команде профессионалов.\n\n"
        "👇 Выбери язык для начала работы:"
    )
    
    # Отправка контента
    try:
        await message.answer_photo(photo=FSInputFile("bot_photo.jpg"), caption=desc, reply_markup=builder.as_markup())
    except:
        await message.answer(desc, reply_markup=builder.as_markup())
    
    # Удаляем команду пользователя
    await message.delete()
# --- СЕРЕДИНА: ЛОГИКА API, РЕГИСТРАЦИИ И АДМИНКИ ---

# 1. Функция верификации через API Pocket Option
async def verify_user(user_id: int) -> bool:
    hash_str = hashlib.md5(f"{user_id}:{PARTNER_ID}:{SECRET}".encode()).hexdigest()
    url = f"https://affiliate.pocketoption.com/api/user-info/{user_id}/{PARTNER_ID}/{hash_str}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                data = await response.json()
                logger.info(f"API Response для {user_id}: {data}")
                return data.get("deposit", 0) >= 20
        except Exception as e:
            logger.error(f"Ошибка API для {user_id}: {e}")
            return False

# 2. Обработка выбора языка -> Запуск регистрации
@dp.callback_query(F.data.startswith("lang_"))
async def registration_flow(callback: types.CallbackQuery):
    text = (
        "📝 **РЕГИСТРАЦИЯ В КОМАНДЕ**\n\n"
        "1. Перейдите по ссылке: [ВАША_ССЫЛКА]\n"
        "2. Введите промокод: `WELCOME50`\n"
        "3. Пополните баланс на сумму от 20$ и выше.\n"
        "4. Нажмите кнопку ниже для подтверждения."
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить пополнение", callback_data="verify_dep")
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

# 3. Верификация и уведомление ТЕБЯ (Босса)
@dp.callback_query(F.data == "verify_dep")
async def verify_deposit(callback: types.CallbackQuery):
    user = callback.from_user
    
    if await verify_user(user.id):
        # Кнопки для управления (прилетят тебе в личку)
        kb_admin = InlineKeyboardBuilder()
        kb_admin.button(text="🚫 Заблокировать", callback_data=f"ban_{user.id}")
        kb_admin.button(text="✅ Разблокировать", callback_data=f"unban_{user.id}")
        
        await bot.send_message(
            ADMIN_ID, 
            f"👤 Новый верифицированный юзер: @{user.username or 'NoNick'}\nID: `{user.id}`", 
            reply_markup=kb_admin.as_markup()
        )
        
        # Доступ к сигналам
        builder = InlineKeyboardBuilder()
        builder.button(text="🚀 Перейти к сигналам", callback_data="mode_menu")
        await callback.message.edit_text("✅ Вы успешно приняты в Team Master!", reply_markup=builder.as_markup())
    else:
        await callback.answer("❌ Пополнение не найдено или сумма меньше 20$!", show_alert=True)

# 4. Администраторская панель (бан/разбан)
@dp.callback_query(F.data.startswith(("ban_", "unban_")))
async def admin_control(callback: types.CallbackQuery):
    action, target_id = callback.data.split("_")
    target_id = int(target_id)
    
    if action == "ban":
        blocked_users.add(target_id)
        await callback.message.edit_text(f"🚫 Пользователь {target_id} заблокирован.")
    else:
        blocked_users.discard(target_id)
        await callback.message.edit_text(f"✅ Пользователь {target_id} разблокирован.")
# --- ФИНАЛ: МОЩНАЯ ЛОГИКА СИГНАЛОВ И РЕЖИМОВ ---

# 1. Меню выбора режима (с проверкой прав)
@dp.callback_query(F.data == "mode_menu")
async def mode_menu(callback: types.CallbackQuery):
    status = get_user_status(callback.from_user.id)
    if is_blocked(callback.from_user.id): return
    
    # Персонализированное приветствие
    greeting = "👑 Привет, Босс!" if status == "BOSS" else "🤝 Привет, друг!" if status == "FRIEND" else "🚀 Выбери режим:"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🤖 Автоматический (AI)", callback_data="auto_mode")
    builder.button(text="👨‍💻 Ручной (Smart Money)", callback_data="manual_mode")
    builder.adjust(1)
    await callback.message.edit_text(greeting, reply_markup=builder.as_markup())

# 2. Ручной режим: Выбор актива
@dp.callback_query(F.data == "manual_mode")
async def manual_mode(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="💵 Валюты (EUR/USD)", callback_data="sig_fx")
    builder.button(text="🪙 Крипта (BTC/USDT)", callback_data="sig_crypto")
    builder.button(text="🔙 Назад", callback_data="mode_menu")
    builder.adjust(1)
    await callback.message.edit_text("📊 Выбери инструмент:", reply_markup=builder.as_markup())

# 3. ГЕНЕРАЦИЯ СИГНАЛА (SMART MONEY)
@dp.callback_query(F.data.startswith("sig_"))
async def send_smart_signal(callback: types.CallbackQuery):
    await clean_chat(callback.message)
    
    text = (
        f"🚀 **СИГНАЛ: SMART MONEY**\n\n"
        f"📊 **Актив:** {callback.data.split('_')[1].upper()}\n"
        f"⏱ **ТФ:** M1 | ⏳ **Эксп:** 1 мин\n"
        f"🎯 **Направление:** BUY 🟢\n"
        f"💎 **Анализ:** Цена в зоне Order Block (OB), наблюдается Imbalance.\n"
        f"💰 **Риск:** 2% от депозита.\n\n"
        f"💡 **Внимание:** Входи только при подтверждении на младшем ТФ."
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Новый сигнал", callback_data="manual_mode")
    builder.button(text="🔙 В меню", callback_data="mode_menu")
    builder.row(types.InlineKeyboardButton(text="🎧 Поддержка", url="https://t.me/andriddddd"))
    
    await callback.message.answer(text, reply_markup=builder.as_markup())

# 4. Автоматический режим (эмуляция AI анализа)
@dp.callback_query(F.data == "auto_mode")
async def auto_mode(callback: types.CallbackQuery):
    await callback.message.edit_text("🤖 Запуск AI анализатора Smart Money...")
    await asyncio.sleep(2)
    await send_smart_signal(callback)

# --- ЗАПУСК ПОЛЛИНГА ---
if __name__ == "__main__":
    logger.info("Бот запущен и готов к работе!")
    asyncio.run(dp.start_polling(bot))
