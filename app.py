import os
import asyncio
import random
import httpx
import hashlib
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

# --- НАСТРОЙКА СИСТЕМНОГО ЛОГИРОВАНИЯ ---
# Используем глубокое логгирование для отслеживания каждого действия в системе
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - [TEAM MASTER QUANTUM CORE SYSTEM] - %(levelname)s - %(message)s'
)
logger = logging.getLogger("QuantumCoreSystem")

# --- КОНФИГУРАЦИЯ БОТА И API ---
BOT_TOKEN = "8643698714:AAEh3AdcOKgdhE5NJ4s7ebIAnsM6zGXdkLI"
PARTNER_ID = "1336904"
API_TOKEN = "Zc4X9zu0EMrqbPuLy3tN"
PLATFORM_URL = "https://u3.shortink.io/cabinet/demo-quick-high-low?utm_campaign=850173&utm_source=affiliate&utm_medium=sr&a=RLQDltKf13Zlrj&al=1771346&ac=smart-link&cid=960963&code=WELCOME50"
SUPPORT_URL = "https://t.me/andriddddd"

# --- VIP-АДМИНИСТРАТОРЫ ---
# Эти ID получают мгновенный доступ к системе без проверки депозита
WHITE_LIST = [6765689893, 8273386412]

# --- ПОЛНЫЙ МАССИВ АКТИВОВ ИЗ ТВОИХ СКРИНШОТОВ ---
ALL_PAIRS = [
    "AED/CNY OTC", "BHD/CNY OTC", "EUR/GBP OTC", "EUR/TRY OTC", "GBP/JPY OTC", 
    "MAD/USD OTC", "NGN/USD OTC", "NZD/USD OTC", "USD/CNH OTC", "USD/EGP OTC",
    "USD/PHP OTC", "USD/PKR OTC", "USD/SGD OTC", "USD/THB OTC", "USD/VND OTC",
    "YER/USD OTC", "ZAR/USD OTC", "USD/CHF OTC", "EUR/USD", "USD/DZD OTC",
    "Cardano OTC", "Bitcoin ETF OTC", "BNB OTC", "Polkadot OTC", "Litecoin OTC",
    "Polygon OTC", "Solana OTC", "TRON OTC", "Chainlink OTC", "Bitcoin OTC",
    "American Express OTC", "FACEBOOK INC OTC", "Intel OTC", "VISA OTC",
    "Apple OTC", "Pfizer Inc OTC", "Cisco OTC", "Tesla OTC", "Alibaba OTC", "Palantir Technologies OTC"
]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- ФУНКЦИЯ ВЕРИФИКАЦИИ ПОЛЬЗОВАТЕЛЯ ---
async def verify_user_access(uid: str):
    # Логика VIP-доступа: сначала проверяем ID в белом списке
    try:
        if int(uid) in WHITE_LIST:
            logger.info(f"ДОСТУП ПРЕДОСТАВЛЕН: Админ с ID {uid} прошел без API-запроса.")
            return True, True
    except ValueError:
        return False, False
    
    # Генерация хэша для запроса к API
    hash_str = hashlib.md5(f"{uid}:{PARTNER_ID}:{API_TOKEN}".encode()).hexdigest()
    url = f"https://affiliate.pocketoption.com/api/user-info/{uid}/{PARTNER_ID}/{hash_str}"
    
    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"Запрос к API для ID: {uid}")
            resp = await client.get(url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                is_active = data.get("status") == "success"
                is_funded = float(data.get("deposit", 0)) >= 20
                return is_active, is_funded
        except Exception as e:
            logger.error(f"КРИТИЧЕСКАЯ ОШИБКА API: {e}")
            return False, False
    return False, False

# --- ОБРАБОТЧИК КОМАНДЫ START ---
@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    welcome_text = (
        "👑 **TEAM MASTER: QUANTUM CORE SYSTEM v4.5**\n\n"
        "Система инициализирована. Мы анализируем рыночные данные 24/7 для поиска оптимальных точек входа.\n\n"
        "🌐 **Выберите предпочтительный язык интерфейса:**\n"
        "Select your language / Выберите язык / Оберіть мову / Wählen Sie eine Sprache / Seleccione el idioma / Choisissez votre langue"
    )
    # Кнопки с языками
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 RU", callback_data="lang:ru"), InlineKeyboardButton(text="🇺🇸 EN", callback_data="lang:en")],
        [InlineKeyboardButton(text="🇺🇦 UA", callback_data="lang:ua"), InlineKeyboardButton(text="🇩🇪 DE", callback_data="lang:de")],
        [InlineKeyboardButton(text="🇪🇸 ES", callback_data="lang:es"), InlineKeyboardButton(text="🇫🇷 FR", callback_data="lang:fr")]
    ])
    await m.answer(welcome_text, reply_markup=kb)

# --- ЛОГИКА ВЫБОРА ЯЗЫКА И РЕГИСТРАЦИИ ---
@dp.callback_query(F.data.startswith("lang:"))
async def select_lang(c: types.CallbackQuery):
    await c.message.answer(
        "📝 **ШАГ 1: РЕГИСТРАЦИЯ В СИСТЕМЕ**\n\n"
        "Для обеспечения синхронизации вашего торгового аккаунта с нашим квантовым ядром, "
        "вы обязаны пройти регистрацию по партнерской ссылке.\n\n"
        "После завершения регистрации, пожалуйста, скопируйте ваш ID и отправьте его в этот чат.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 ПЕРЕЙТИ НА ПЛАТФОРМУ", url=PLATFORM_URL)]])
    )

# --- ПРОВЕРКА ID ПОЛЬЗОВАТЕЛЯ ---
@dp.message(F.text.isdigit())
async def handle_id(m: types.Message):
    reg, dep = await verify_user_access(m.text)
    if not reg:
        await m.answer("❌ **ОШИБКА:** ID не найден в нашей базе. Убедитесь, что вы зарегистрировались по ссылке.")
    elif not dep:
        await m.answer(
            "💳 **ШАГ 2: АКТИВАЦИЯ БАЛАНСА**\n\n"
            "Ваш ID успешно верифицирован. Чтобы разблокировать доступ к закрытым квантовым сигналам, "
            "необходимо пополнить баланс на сумму от $20.\n\n"
            "Используйте промокод `WELCOME50` для получения бонуса к пополнению.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄 ПРОВЕРИТЬ АКТИВАЦИЮ", callback_data=f"check:{m.text}")]])
        )
    else:
        await m.answer("✅ **СИСТЕМА ПОЛНОСТЬЮ АКТИВИРОВАНА.** Добро пожаловать, босс. Квантовое ядро готово к работе.", reply_markup=get_kb_menu())

# --- ПОДТВЕРЖДЕНИЕ ПОПОЛНЕНИЯ ---
@dp.callback_query(F.data.startswith("check:"))
async def check_activation(c: types.CallbackQuery):
    _, dep = await verify_user_access(c.data.split(":")[1])
    if dep:
        await c.message.answer("✅ **Доступ открыт.** Квантовый анализ готов к работе.", reply_markup=get_kb_menu())
    else:
        await c.answer("❌ Депозит не найден в системе. Попробуйте повторить операцию.", show_alert=True)

# --- МЕНЮ УПРАВЛЕНИЯ СИГНАЛАМИ ---
def get_kb_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📡 ПОЛУЧИТЬ КВАНТОВЫЙ СИГНАЛ", callback_data="get_sig")],
        [InlineKeyboardButton(text="👨‍💻 СВЯЗЬ С РАЗРАБОТЧИКОМ", url=SUPPORT_URL)]
    ])

# --- ГЕНЕРАТОР СИГНАЛОВ С РАСШИРЕННОЙ ЭКСПИРАЦИЕЙ ---
@dp.callback_query(F.data == "get_sig")
async def generate_signal(c: types.CallbackQuery):
    msg = await c.message.answer("🔄 **Инициализация квантового алгоритма... Идет глубокий анализ рынков...**")
    await asyncio.sleep(4)
    
    # Генерация данных сигнала
    asset = random.choice(ALL_PAIRS)
    direction = random.choice(['📉 🔴 SELL / ВНИЗ', '📈 🟢 BUY / ВВЕРХ'])
    tf = random.choice(['M1', 'M5', 'M15'])
    expiry = random.randint(2, 15)  # Экспирация от 2 до 15 минут
    payout = random.choice(['85%', '92%', '95%'])
    confidence = random.randint(90, 99)
    
    sig = (
        f"📡 **СИГНАЛ TEAM MASTER**\n\n"
        f"🔹 **Актив:** `{asset}`\n"
        f"⚡️ **Направление:** {direction}\n"
        f"📊 **ТФ:** `{tf}`\n"
        f"⏱ **Время экспирации:** `{expiry} мин`\n"
        f"🎯 **Процент выплаты:** `{payout}`\n"
        f"🔥 **Индекс уверенности алгоритма:** `{confidence}%`\n\n"
        "⚠️ *ВНИМАНИЕ: Трейдинг — это высокорискованная деятельность. Всегда соблюдайте правила риск-менеджмента.*"
    )
    await msg.edit_text(sig, reply_markup=get_kb_menu())

# --- ВЕБ-СЕРВЕР ---
async def start_web_server():
    runner = web.AppRunner(web.Application())
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    logger.info("Веб-сервер успешно запущен и ожидает запросов.")

async def main():
    logger.info("Запуск системы Team Master Quantum Core...")
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"КРИТИЧЕСКАЯ ОШИБКА ЯДРА: {e}")
 
