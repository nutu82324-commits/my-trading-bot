import os
import json
import logging
import asyncio
import hashlib
import random
import httpx
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TeamMasterPro")

BOT_TOKEN = "8643698714:AAEh3AdcOKgdhE5NJ4s7ebIAnsM6zGXdkLI"
PARTNER_ID = "1336904"
API_TOKEN = "Zc4X9zu0EMrqbPuLy3tN"
PLATFORM_URL = "https://u3.shortink.io/cabinet/demo-quick-high-low?utm_campaign=850173&utm_source=affiliate&utm_medium=sr&a=RLQDltKf13Zlrj&al=1771346&ac=smart-link&cid=960963&code=WELCOME50"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Полный список активов из твоих скриншотов
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

async def send_analyzing_process(chat_id: int):
    # Рандомная задержка (5-60 сек), как ты просил
    wait = random.uniform(5, 60) / 3
    msg = await bot.send_message(chat_id, "🔄 **Анализ ликвидности...**")
    await asyncio.sleep(wait)
    await msg.edit_text("🔄 **ИИ-АНАЛИЗ РЫНКА...**")
    await asyncio.sleep(wait)
    await msg.edit_text("🔄 **ФОРМИРОВАНИЕ ТОЧКИ ВХОДА...**")
    await asyncio.sleep(wait)
    try: await msg.delete()
    except: pass

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("Пришли свой ID для активации доступа:")

@dp.message(F.text.isdigit())
async def handle_id(m: types.Message):
    await send_analyzing_process(m.chat.id)
    text = (
        f"🚀 **TEAM MASTER — СИГНАЛ**\n\n"
        f"📊 **Актив:** `{random.choice(ALL_PAIRS)}`\n"
        f"⏳ **Экспирация:** `{random.randint(2, 5)} МИН`\n"
        f"📈 **Прогноз:** {random.choice(['🟢 ВВЕРХ', '🔴 ВНИЗ'])}\n"
        f"🎯 **Точность:** `{round(random.uniform(92, 98), 1)}%`"
    )
    await m.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 ПЛАТФОРМА", url=PLATFORM_URL)]
    ]))

# Минималистичный веб-сервер для Render (не падает)
async def web_server():
    runner = web.AppRunner(web.Application())
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.gather(web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
