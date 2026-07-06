import hashlib
import aiohttp
import asyncio
import logging
import sys
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from aiogram.client.default import DefaultBotProperties

# --- ⚙️ КОНФИГУРАЦИЯ СИСТЕМЫ ---
BOT_TOKEN = "8479849828:AAEl31VYsy9o7NrSL9lIHdmHDaUBrbP1aFw"
ADMIN_ID = 6765689893       # Твой ID
WHITE_LIST = {8273386412}   # ID Друга
PARTNER_ID = 'ВАШ_PARTNER_ID'
SECRET = 'Zc4X9zu0EMrqbPuLy3tN'

# --- 🪵 ПРОФЕССИОНАЛЬНОЕ ЛОГИРОВАНИЕ ---
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] | %(levelname)s | %(name)s | %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("TeamMasterAI")

# --- 🚀 ИНИЦИАЛИЗАЦИЯ ---
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()
blocked_users = set()

# --- 🛡 ФУНКЦИИ БЕЗОПАСНОСТИ И АНАЛИЗА ---
def get_user_status(user_id: int) -> str:
    if user_id == ADMIN_ID: return "BOSS"
    if user_id in WHITE_LIST: return "FRIEND"
    return "USER"

def is_blocked(user_id: int) -> bool:
    return user_id in blocked_users

def get_strategy_analysis(strategy_key: str) -> str:
    """Генерация профессионального контекста по методологиям"""
    data = {
        "sig_smart": "Цена находится в зоне интереса (Order Block). Ожидается реакция институционального капитала. FVG (имбаланс) подтверждает намерение.",
        "sig_ict": "Silver Bullet Time: Ожидаем Market Structure Shift (MSS) после снятия ликвидности (Liquidity Sweep) в окне 02:00-03:00.",
        "sig_turtle": "Цена совершила ложный пробой локального экстремума. Ожидается возврат к средней (Mean Reversion) и продолжение движения в канале.",
        "sig_breaker": "Произошла девиация и слом структуры через Breaker Block. Уровень поддержки подтвержден как новый уровень сопротивления."
    }
    return data.get(strategy_key, "Аналитический алгоритм в режиме ожидания...")

async def clean_chat(message: types.Message):
    try: await message.delete()
    except: pass

# --- 👋 СТАРТОВАЯ ЛОГИКА (WELCOME SCREEN) ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user = message.from_user
    logger.info(f"Вход в систему: ID {user.id} | Роль: {get_user_status(user.id)}")
    
    if is_blocked(user.id): return

    # Описание бота
    desc = (
        "🤖 *TEAM MASTER | INSTITUTIONAL AI*\n\n"
        "Приветствую, трейдер. Ты получил доступ к закрытому алгоритму анализа рынка. "
        "Наша нейросеть специализируется на поиске входов по методологиям:\n\n"
        "🎯 *Smart Money Concepts*\n"
        "⏱ *ICT Silver Bullet*\n"
        "🐢 *Turtle Soup Analysis*\n"
        "🧱 *Breaker Block Reversal*\n\n"
        "Выбери стратегию для получения сигнала:"
    )
    
    # Кнопки
    builder = InlineKeyboardBuilder()
    builder.button(text="🎯 Smart Money", callback_data="sig_smart")
    builder.button(text="⏱ ICT Silver Bullet", callback_data="sig_ict")
    builder.button(text="🐢 Turtle Soup", callback_data="sig_turtle")
    builder.button(text="🧱 Breaker Block", callback_data="sig_breaker")
    builder.adjust(1)
    
    # Отправка фото + текст
    try:
        await message.answer_photo(
            photo=FSInputFile("IMG_20260601_135650_803.jpg"), 
            caption=desc, 
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logger.error(f"Ошибка загрузки фото: {e}")
        await message.answer(desc, reply_markup=builder.as_markup())
    
    await clean_chat(message)
# --- ⚙️ СЕРЕДИНА: API, ВЕРИФИКАЦИЯ И АДМИНКА ---

# Функция проверки депозита через API
async def verify_user(user_id: int) -> bool:
    hash_str = hashlib.md5(f"{user_id}:{PARTNER_ID}:{SECRET}".encode()).hexdigest()
    url = f"https://affiliate.pocketoption.com/api/user-info/{user_id}/{PARTNER_ID}/{hash_str}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                data = await response.json()
                logger.info(f"API Check для {user_id}: {data}")
                return data.get("deposit", 0) >= 20
        except Exception as e:
            logger.error(f"Ошибка API: {e}")
            return False

# Обработка клика по стратегии -> Проверка статуса
@dp.callback_query(F.data.startswith("sig_"))
async def strategy_selection(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    # Если ты или друг — пускаем сразу, если юзер — проверяем депо
    if get_user_status(user_id) == "USER":
        if not await verify_user(user_id):
            await callback.answer("❌ Доступ закрыт! Пополните баланс от 20$.", show_alert=True)
            return
    
    # Если всё ок, переходим к генерации сигнала
    strategy_key = callback.data
    analysis_text = get_strategy_analysis(strategy_key)
    
    # Формируем ответ с сигналом
    signal_msg = (
        f"🚀 *СИГНАЛ: {callback.data.replace('sig_', '').upper()}*\n\n"
        f"💎 *Технический анализ:*\n{analysis_text}\n\n"
        f"📉 *Актив:* EUR/USD | ⏱ *Эксп:* 1 минута"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Обновить анализ", callback_data=strategy_key)
    builder.button(text="🔙 В меню стратегий", callback_data="start") # Возврат в начало
    builder.adjust(1)
    
    await callback.message.edit_text(signal_msg, reply_markup=builder.as_markup())

# Админ-панель: управление банами
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🚫 Блокировка пользователя", callback_data="admin_ban")
    builder.button(text="📊 Статистика бота", callback_data="admin_stats")
    await message.answer("🛠 Панель управления Team Master:", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "admin_ban")
async def ban_mode(callback: types.CallbackQuery):
    await callback.message.edit_text("Введите ID пользователя для бана (например: /ban 12345678)")

@dp.message(Command("ban"))
async def ban_user(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    try:
        user_id = int(message.text.split()[1])
        blocked_users.add(user_id)
        await message.answer(f"✅ Пользователь {user_id} заблокирован в системе.")
    except:
        await message.answer("❌ Ошибка. Формат: /ban ID")
# --- ПОЛНЫЙ СПИСОК АКТИВОВ И ЛОГИКА ---
ASSETS = {
    "Валюты": [
        "AUD/USD OTC", "CAD/CHF OTC", "EUR/GBP OTC", "EUR/JPY OTC", "EUR/USD OTC", 
        "NZD/USD OTC", "SAR/CNY OTC", "UAH/USD OTC", "USD/BDT OTC", "USD/CAD OTC",
        "USD/CLP OTC", "USD/IDR OTC", "USD/INR OTC", "USD/JPY OTC", "USD/SGD OTC",
        "ZAR/USD OTC", "EUR/HUF OTC", "AUD/CHF", "CAD/CHF", "EUR/USD", 
        "KES/USD OTC", "USD/CHF", "USD/COP OTC", "EUR/NZD OTC", "USD/PHP OTC",
        "JOD/CNY OTC", "AED/CNY OTC", "QAR/CNY OTC", "YER/USD OTC", "AUD/JPY",
        "CHF/JPY OTC", "AUD/USD", "USD/CAD", "AED/CNY OTC", "AUD/CAD", 
        "AUD/NZD OTC", "USD/THB OTC", "GBP/USD", "CAD/JPY", "EUR/CAD", 
        "USD/JPY", "GBP/JPY", "GBP/CAD", "NZD/JPY OTC", "CHF/NOK OTC", 
        "EUR/JPY", "EUR/TRY OTC", "USD/BRL OTC", "AUD/CAD OTC", "EUR/CHF OTC", 
        "GBP/AUD", "AUD/CHF OTC", "CAD/JPY OTC", "GBP/AUD OTC", "NGN/USD OTC", 
        "USD/DZD OTC", "USD/ARS OTC", "USD/CNH OTC", "EUR/CHF"
    ],
    "Криптовалюта": [
        "Cardano OTC", "Dogecoin OTC", "Polkadot OTC", "Polygon OTC", "Toncoin OTC", 
        "Ethereum OTC", "BNB OTC", "Avalanche OTC", "Solana OTC", "Bitcoin OTC"
    ],
    "Акции": [
        "Apple OTC", "Boeing Company OTC", "McDonald's OTC", "Pfizer Inc OTC", "VISA OTC", 
        "Cisco OTC", "GameStop Corp OTC", "ExxonMobil OTC", "Tesla OTC", "Citigroup Inc OTC",
        "Netflix OTC", "American Express OTC", "Amazon OTC", "Palantir Technologies OTC", 
        "Alibaba OTC", "VIX OTC", "Coinbase Global OTC", "Boeing Company", "FACEBOOK INC", "FACEBOOK INC OTC"
    ]
}

def is_market_open():
    return datetime.datetime.now().weekday() < 5

async def send_fancy_signal(callback: types.CallbackQuery, asset: str):
    is_live = "OTC" not in asset
    if not is_market_open() and is_live:
        await callback.answer("❌ Живой рынок закрыт в выходные! Выберите актив OTC.", show_alert=True)
        return

    await callback.message.edit_text("🔄 *Инициализация алгоритма...*")
    await asyncio.sleep(0.5)
    await callback.message.edit_text("🔄 *Анализ рыночных объемов...*")
    await asyncio.sleep(0.5)
    
    exp = "1 минута" if is_live else "3 минуты"
    analysis = get_strategy_analysis("sig_smart")
    
    signal_text = (
        f"👑 *TEAM MASTER SIGNAL*\n\n"
        f"📊 *Актив:* `{asset}`\n"
        f"⏱ *Таймфрейм:* M1\n"
        f"⏳ *Экспирация:* {exp}\n"
        f"🎯 *Прогноз:* BUY 🟢\n\n"
        f"💎 *Технический разбор:*\n{analysis}\n\n"
        f"⚠️ *Соблюдай риск-менеджмент!*"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Обновить анализ", callback_data=f"sig_{asset.replace(' ', '_')}")
    builder.button(text="🔙 К выбору активов", callback_data="mode_manual")
    builder.adjust(1)
    
    await callback.message.edit_text(signal_text, reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("sig_"))
async def process_signal(callback: types.CallbackQuery):
    asset = callback.data.replace("sig_", "").replace("_", " ")
    await send_fancy_signal(callback, asset)
