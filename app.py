import os
import json
import logging
import asyncio
import hashlib
from datetime import datetime, timedelta
import random
import httpx
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TeamMasterAuto")

# --- КОНФИГУРАЦИЯ СЕТИ И ПАРТНЕРКИ ---
BOT_TOKEN = "8643698714:AAEh3AdcOKgdhE5NJ4s7ebIAnsM6zGXdkLI"
DB_FILE = "requests.json"

ADMIN_IDS = [6765689893]  
VIP_IDS = [8273386412]

PARTNER_ID = "1336904"
API_TOKEN = "Zc4X9zu0EMrqbPuLy3tN"
PLATFORM_URL = "https://u3.shortink.io/cabinet/demo-quick-high-low?utm_campaign=850173&utm_source=affiliate&utm_medium=sr&a=RLQDltKf13Zlrj&al=1771346&ac=smart-link&cid=960963&code=WELCOME50" 

SUPPORT_URL = "https://t.me/andriddddd"       
TELEGRAM_CHANNEL = "https://t.me/+uekq4TquqkM4Mzcy" 
PHOTO_URL = "https://i.ibb.co/L1yZ6Gz/team-master-cover.jpg"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- ВЕБ-СЕРВЕР ---
async def handle(request):
    return web.Response(text="Bot is alive!")

async def start_webhook():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Веб-сервер запущен на порту {port}")

# --- БАЗА ДАННЫХ И API ---
def get_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {"users": {}}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def generate_api_hash(user_id: str) -> str:
    hash_string = f"{user_id}:{PARTNER_ID}:{API_TOKEN}"
    return hashlib.md5(hash_string.encode('utf-8')).hexdigest()

async def check_pocket_api_full(user_id: str) -> tuple[bool, bool]:
    api_hash = generate_api_hash(user_id)
    url = f"https://affiliate.pocketoption.com/api/user-info/{user_id}/{PARTNER_ID}/{api_hash}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                deposit_amount = float(data.get("deposit", 0))
                return True, deposit_amount >= 20
        except Exception as e:
            logger.error(f"API Error: {e}")
    return False, False

# --- АКТИВЫ И ГЕНЕРАЦИЯ ---
ALL_PAIRS = [
    "AED/CNY OTC", "BHD/CNY OTC", "EUR/GBP OTC", "EUR/TRY OTC", "GBP/JPY OTC", 
    "MAD/USD OTC", "NGN/USD OTC", "NZD/USD OTC", "USD/CNH OTC", "USD/EGP OTC",
    "USD/PHP OTC", "USD/PKR OTC", "USD/SGD OTC", "USD/THB OTC", "USD/VND OTC",
    "YER/USD OTC", "ZAR/USD OTC", "USD/CHF OTC", "EUR/USD", "USD/DZD OTC",
    "Cardano OTC", "Bitcoin ETF OTC", "BNB OTC", "Polkadot OTC", "Litecoin OTC",
    "Polygon OTC", "Solana OTC", "TRON OTC", "Chainlink OTC", "Bitcoin OTC",
    "American Express OTC", "FACEBOOK INC OTC", "Intel OTC", "VISA OTC",
    "Apple OTC", "Pfizer Inc OTC", "Cisco OTC", "Tesla OTC", "Alibaba OTC",
    "Palantir Technologies OTC"
]

def generate_signal_text() -> str:
    selected_pair = random.choice(ALL_PAIRS)
    direction = random.choice(["🟢 ВВЕРХ / CALL", "🔴 ВНИЗ / PUT"])
    timeframe = random.randint(2, 5)  # Экспирация от 2 до 5 минут
    accuracy = round(random.uniform(91.4, 96.2), 1)

    return (
        f"🚀 **TEAM MASTER — СИГНАЛ СФОРМИРОВАН** 🚀\n\n"
        f"📊 **Активный актив:** `{selected_pair}`\n"
        f"⏳ **Интервал / Экспирация:** `{timeframe} МИНУТ` \n"
        f"📈 **Направление сделки:** {direction}\n"
        f"🎯 **Уверенность ИИ-алгоритма:** `{accuracy}%`\n\n"
        f"⚠️ *Входите в сделку строго по времени. Соблюдайте риск-менеджмент!*"
    )

def get_signal_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 ОТКРЫТЬ POCKET OPTION", url=PLATFORM_URL)],
        [InlineKeyboardButton(text="📢 НАШ ТЕЛЕГРАМ КАНАЛ", url=TELEGRAM_CHANNEL)],
        [InlineKeyboardButton(text="👨‍💻 РАЗРАБОТЧИК / SUPPORT", url=SUPPORT_URL)],
        [InlineKeyboardButton(text="🔄 СЛЕДУЮЩИЙ СИГНАЛ", callback_data="next_signal")]
    ])

async def send_analyzing_process(chat_id: int, bot_instance: Bot):
    p = random.sample(ALL_PAIRS, 3)
    msg = await bot_instance.send_message(chat_id, f"🔄 **HROM QUANTUM CORE v18.0 запущено...**\n⌛ Сканирование `{p[0]}`")
    await asyncio.sleep(1.2)
    await msg.edit_text(f"🔄 **ИИ-АНАЛИЗ РЫНКА...**\n⌛ Проверка объемов на `{p[1]}`")
    await asyncio.sleep(1.2)
    await msg.edit_text(f"🔄 **ФОРМИРОВАНИЕ ТОЧКИ ВХОДА...**\n⌛ Расчет профита на `{p[2]}`")
    await asyncio.sleep(1.0)
    try: await msg.delete()
    except: pass

# --- ОБРАБОТЧИКИ СООБЩЕНИЙ ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id in ADMIN_IDS or message.from_user.id in VIP_IDS:
        await send_analyzing_process(message.chat.id, bot)
        await message.answer(generate_signal_text(), reply_markup=get_signal_keyboard(), parse_mode="Markdown")
        return
    
    await message.answer_photo(photo=PHOTO_URL, caption="📈 **TEAM MASTER GLOBAL BOT**\n\nВыберите язык:", 
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                   [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"), InlineKeyboardButton(text="🇺🇸 English", callback_data="lang:en")]
                               ]))

@dp.callback_query(F.data.startswith("lang:"))
async def process_lang(callback: types.CallbackQuery):
    db = get_db()
    db["users"][f"id_{callback.from_user.id}"] = {"status": "registering", "chat_id": callback.message.chat.id}
    save_db(db)
    await callback.message.answer("Введите ваш ID с платформы для активации:")
    await callback.answer()

@dp.message(F.text)
async def handle_id_input(message: types.Message):
    user_input = message.text.strip()
    if not user_input.isdigit(): return

    # Проверка системы защиты
    is_ref_ok, is_deposit_ok = await check_pocket_api_full(user_input)
    
    if not is_ref_ok:
        await message.answer("❌ ID не найден. Зарегистрируйтесь по ссылке.")
        return

    if is_deposit_ok:
        await send_analyzing_process(message.chat.id, bot)
        await message.answer(generate_signal_text(), reply_markup=get_signal_keyboard(), parse_mode="Markdown")
    else:
        await message.answer("💳 Пополните баланс от $20 для активации.")

@dp.callback_query(F.data == "next_signal")
async def process_next_signal(callback: types.CallbackQuery):
    await send_analyzing_process(callback.message.chat.id, bot)
    await callback.message.answer(generate_signal_text(), reply_markup=get_signal_keyboard(), parse_mode="Markdown")
    await callback.answer()

async def main():
    asyncio.create_task(start_webhook())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
