import os
import asyncio
import random
import httpx
import hashlib
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- НАСТРОЙКА ЛОГИРОВАНИЯ ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TeamMasterQuantumCore")

# --- КОНФИГУРАЦИЯ ---
BOT_TOKEN = "8643698714:AAEh3AdcOKgdhE5NJ4s7ebIAnsM6zGXdkLI"
PARTNER_ID = "1336904"
API_TOKEN = "Zc4X9zu0EMrqbPuLy3tN"
PLATFORM_URL = "https://u3.shortink.io/cabinet/demo-quick-high-low?utm_campaign=850173&utm_source=affiliate&utm_medium=sr&a=RLQDltKf13Zlrj&al=1771346&ac=smart-link&cid=960963&code=WELCOME50"
SUPPORT_URL = "https://t.me/andriddddd"

# VIP-СПИСОК (АДМИНЫ)
WHITE_LIST = [6765689893, 8273386412]

# РАСШИРЕННЫЙ СПИСОК АКТИВОВ
ALL_PAIRS = [
    "Bitcoin OTC", "EUR/USD", "GBP/JPY OTC", "Tesla OTC", "Apple OTC", 
    "Gold OTC", "BNB OTC", "USD/CHF OTC", "S&P 500 OTC", "Netflix OTC",
    "Ethereum OTC", "Silver OTC", "CAD/JPY OTC", "AUD/NZD OTC"
]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- ФУНКЦИЯ ПРОВЕРКИ С API ---
async def verify_user_access(uid: str):
    # Приоритет VIP
    if int(uid) in WHITE_LIST:
        return True, True
    
    # Генерация хэша для запроса
    hash_str = hashlib.md5(f"{uid}:{PARTNER_ID}:{API_TOKEN}".encode()).hexdigest()
    url = f"https://affiliate.pocketoption.com/api/user-info/{uid}/{PARTNER_ID}/{hash_str}"
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                is_active = data.get("status") == "success"
                is_funded = float(data.get("deposit", 0)) >= 20
                return is_active, is_funded
        except Exception as e:
            logger.error(f"Ошибка проверки API: {e}")
            return False, False
    return False, False

# --- ОБРАБОТЧИК START ---
@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    welcome_text = (
        "👑 **TEAM MASTER: QUANTUM CORE SYSTEM v2.5**\n\n"
        "Мы предоставляем профессиональный алгоритмический анализ рынков в режиме реального времени.\n\n"
        "📈 **ИНСТРУКЦИЯ ДЛЯ ТРЕЙДЕРА:**\n"
        "1. Зарегистрируйтесь по официальной ссылке.\n"
        "2. Пройдите процедуру верификации ID.\n"
        "3. Активируйте торговый баланс.\n"
        "4. Получайте точные сигналы с точностью до 99%.\n\n"
        "⚠️ *Не нарушайте мани-менеджмент. Торгуйте с умом.*"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 RU", callback_data="lang:ru"), InlineKeyboardButton(text="🇺🇸 EN", callback_data="lang:en")],
        [InlineKeyboardButton(text="🇺🇦 UA", callback_data="lang:ua"), InlineKeyboardButton(text="🇩🇪 DE", callback_data="lang:de")],
        [InlineKeyboardButton(text="🇪🇸 ES", callback_data="lang:es"), InlineKeyboardButton(text="🇫🇷 FR", callback_data="lang:fr")]
    ])
    await m.answer(welcome_text, reply_markup=kb)

# --- ЛОГИКА РЕГИСТРАЦИИ ---
@dp.callback_query(F.data.startswith("lang:"))
async def select_lang(c: types.CallbackQuery):
    await c.message.answer(
        "📝 **ШАГ 1: РЕГИСТРАЦИЯ В СИСТЕМЕ**\n\n"
        "Для подключения вашего аккаунта к нашему квантовому ядру необходимо "
        "зарегистрироваться по партнерской ссылке ниже.\n\n"
        "После регистрации пришлите свой ID (цифры) в данный чат.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 ПЕРЕЙТИ НА ПЛАТФОРМУ", url=PLATFORM_URL)]])
    )

# --- ПРОВЕРКА ID ---
@dp.message(F.text.isdigit())
async def handle_id(m: types.Message):
    reg, dep = await verify_user_access(m.text)
    if not reg:
        await m.answer("❌ **Ошибка:** ID не найден в базе. Используйте правильную ссылку.")
    elif not dep:
        await m.answer(
            "💳 **ШАГ 2: АКТИВАЦИЯ БАЛАНСА**\n\n"
            "Ваш ID верифицирован. Для доступа к закрытым сигналам пополните баланс от $20. "
            "Используйте промокод `WELCOME50` для бонуса.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄 ПРОВЕРИТЬ АКТИВАЦИЮ", callback_data=f"check:{m.text}")]])
        )
    else:
        await m.answer("✅ **СИСТЕМА УСПЕШНО АКТИВИРОВАНА.** Добро пожаловать, босс.", reply_markup=get_kb_menu())

@dp.callback_query(F.data.startswith("check:"))
async def check_activation(c: types.CallbackQuery):
    _, dep = await verify_user_access(c.data.split(":")[1])
    if dep:
        await c.message.answer("✅ **Доступ открыт.** Квантовый анализ готов к работе.", reply_markup=get_kb_menu())
    else:
        await c.answer("❌ Депозит не найден.", show_alert=True)

# --- МЕНЮ СИГНАЛОВ ---
def get_kb_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📡 ПОЛУЧИТЬ КВАНТОВЫЙ СИГНАЛ", callback_data="get_sig")],
        [InlineKeyboardButton(text="👨‍💻 ПОДДЕРЖКА / РАЗРАБОТЧИК", url=SUPPORT_URL)]
    ])

@dp.callback_query(F.data == "get_sig")
async def generate_signal(c: types.CallbackQuery):
    msg = await c.message.answer("🔄 **Инициализация квантового алгоритма...**")
    await asyncio.sleep(4)
    sig = (
        f"📡 **СИГНАЛ TEAM MASTER**\n\n"
        f"🔹 **Активы:** `{random.choice(ALL_PAIRS)}`\n"
        f"⚡️ **Направление:** {random.choice(['📉 🔴 SELL', '📈 🟢 BUY'])}\n"
        f"📊 **ТФ:** `{random.choice(['M1', 'M3', 'M5'])}`\n"
        f"⏱ **Время экспирации:** `{random.randint(1, 5)} мин`\n"
        f"🎯 **Выплата:** `{random.choice(['85%', '92%'])}`\n"
        f"🔥 **Уверенность алгоритма:** `{random.randint(90, 99)}%`\n\n"
        "⚠️ *Трейдинг требует дисциплины. Соблюдайте риск-менеджмент.*"
    )
    await msg.edit_text(sig, reply_markup=get_kb_menu())

# --- ВЕБ-СЕРВЕР ---
async def start_web_server():
    runner = web.AppRunner(web.Application())
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    logger.info("Веб-сервер запущен.")

async def main():
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
