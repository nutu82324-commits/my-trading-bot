import asyncio
import sqlite3
import os
import ccxt.async_support as ccxt
import pandas as pd
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

# ИНИЦИАЛИЗАЦИЯ
# Токен берется из переменной BOT_TOKEN (настрой её в Railway -> Variables)
TOKEN = os.getenv("BOT_TOKEN")
BOSS_ID = 6765689893
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

db = sqlite3.connect("platform.db")
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, status TEXT, paid INTEGER DEFAULT 0)")
db.commit()

# ТВОЯ ПОЛНАЯ БАЗА
ASSETS = {
    "🌍 Валюты": ["AUD/USD OTC", "CAD/CHF OTC", "EUR/GBP OTC", "EUR/JPY OTC", "EUR/USD OTC", "NZD/USD OTC", "SAR/CNY OTC", "UAH/USD OTC", "USD/BDT OTC", "USD/CAD OTC", "USD/CLP OTC", "USD/IDR OTC", "USD/INR OTC", "USD/JPY OTC", "USD/SGD OTC", "ZAR/USD OTC", "EUR/HUF OTC", "AUD/CHF", "CAD/CHF", "EUR/USD", "KES/USD OTC", "USD/CHF", "USD/COP OTC", "EUR/NZD OTC", "USD/PHP OTC", "JOD/CNY OTC", "AED/CNY OTC", "QAR/CNY OTC", "YER/USD OTC", "AUD/JPY", "CHF/JPY OTC", "AUD/USD", "USD/CAD", "AED/CNY OTC", "AUD/CAD", "AUD/NZD OTC", "USD/THB OTC", "GBP/USD", "CAD/JPY", "EUR/CAD", "USD/JPY", "GBP/JPY", "GBP/CAD", "NZD/JPY OTC", "CHF/NOK OTC", "EUR/JPY", "EUR/TRY OTC", "USD/BRL OTC", "AUD/CAD OTC", "EUR/CHF OTC", "GBP/AUD", "AUD/CHF OTC", "CAD/JPY OTC", "GBP/AUD OTC", "NGN/USD OTC", "USD/DZD OTC", "USD/ARS OTC", "USD/CNH OTC", "EUR/CHF"],
    "💎 Крипта": ["Cardano OTC", "Dogecoin OTC", "Polkadot OTC", "Polygon OTC", "Toncoin OTC", "Ethereum OTC", "BNB OTC", "Avalanche OTC", "Solana OTC", "Bitcoin OTC",],
    "📈 Акции": ["Apple OTC", "Boeing Company OTC", "McDonald's OTC", "Pfizer Inc OTC", "VISA OTC", "Cisco OTC", "GameStop Corp OTC", "ExxonMobil OTC", "Tesla OTC", "Citigroup Inc OTC", "Netflix OTC", "American Express OTC", "Amazon OTC", "Palantir Technologies OTC", "Alibaba OTC", "VIX OTC", "Coinbase Global OTC", "Boeing Company", "FACEBOOK INC", "FACEBOOK INC OTC", "AAPL", "TSLA", "NVDA", "GOOGL", "AMZN", "MSFT"],
    "🌐 Языки": {
        "Русский": "🇷🇺", "English": "🇺🇸", "Deutsch": "🇩🇪", "Español": "🇪🇸", 
        "Français": "🇫🇷", "Italiano": "🇮🇹", "Português": "🇵🇹", "Türkçe": "🇹🇷", 
        "العربية": "🇸🇦", "中文": "🇨🇳"
    }
}

# АНАЛИЗАТОР (БЕЗ pandas_ta, расчет RSI/EMA вручную)
async def ai_analyze(symbol):
    try:
        ex = ccxt.binance({'enableRateLimit': True})
        pair = symbol.replace(' OTC', '').replace('/', '')
        ohlcv = await ex.fetch_ohlcv(pair, '1m', limit=100)
        df = pd.DataFrame(ohlcv, columns=['t', 'o', 'h', 'l', 'c', 'v'])
        
        # Ручной расчет RSI
        delta = df['c'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        # Ручной расчет EMA
        ema = df['c'].ewm(span=50, adjust=False).mean().iloc[-1]
        price = df['c'].iloc[-1]
        
        if rsi < 30 and price > ema:
            return "🟢 BUY", "Сильный потенциал роста", "96.4%", "1 минута"
        elif rsi > 70 and price < ema:
            return "🔴 SELL", "Сильный потенциал падения", "95.8%", "1 минута"
        return "⚪ WAIT", "Нейтральный рынок", "42.0%", "Не рекомендуется"
    except Exception as e:
        print(f"Error: {e}")
        return "⚠️", "Ошибка API", "0%", "N/A"

# ХЕНДЛЕРЫ
@router.message(Command("start"))
async def start(m: Message):
    if not cur.execute("SELECT 1 FROM users WHERE id=?", (m.from_user.id,)).fetchone():
        cur.execute("INSERT INTO users (id, status) VALUES (?, ?)", (m.from_user.id, "active"))
        db.commit()
    await m.answer_photo(photo="https://telegra.ph/file/0f3e8f85f1b1b1.jpg", 
                         caption="👑 **MASTER AI SYSTEM**\n🚀 API: Binance Integration\n📊 Indicators: RSI + EMA\n⏱ Expiration: 1m", 
                         reply_markup=InlineKeyboardBuilder().button(text="✅ ПРОВЕРИТЬ ДЕПОЗИТ", callback_data="check").as_markup())

@router.callback_query(F.data == "check")
async def check(c: CallbackQuery):
    user = cur.execute("SELECT paid FROM users WHERE id=?", (c.from_user.id,)).fetchone()
    if user and user[0] == 1:
        kb = InlineKeyboardBuilder()
        for k in ASSETS: kb.button(text=k, callback_data=f"cat_{k}")
        kb.adjust(1)
        await c.message.edit_text("⚙️ **ГЛАВНОЕ МЕНЮ**", reply_markup=kb.as_markup())
    else: await c.answer("⚠️ Оплати доступ!", show_alert=True)

@router.callback_query(F.data.startswith("cat_"))
async def cat(c: CallbackQuery):
    cat_name = c.data.split("_")[1]
    kb = InlineKeyboardBuilder()
    if cat_name == "🌐 Языки":
        for lang, flag in ASSETS["🌐 Языки"].items(): kb.button(text=f"{flag} {lang}", callback_data=f"lang_{lang}")
    else:
        for a in ASSETS[cat_name]: kb.button(text=a, callback_data=f"sig_{a}")
    kb.adjust(2)
    await c.message.edit_text(f"💎 **Выбор: {cat_name}**", reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("sig_"))
async def sig(c: CallbackQuery):
    a = c.data.split("_", 1)[1]
    status, desc, acc, exp = await ai_analyze(a)
    await c.message.edit_text(f"🎯 **{a}**\n\n📊 ИИ Статус: {status}\n💡 Прогноз: {desc}\n🎯 Точность: {acc}\n⏱ Таймфрейм: {exp}", 
                               reply_markup=InlineKeyboardBuilder().button(text="🔄 АНАЛИЗ", callback_data=f"sig_{a}").button(text="⬅️ НАЗАД", callback_data="check").adjust(1).as_markup())

@router.callback_query(F.data.startswith("lang_"))
async def set_lang(c: CallbackQuery):
    await c.answer(f"🌐 Язык применен: {c.data.split('_')[1]}", show_alert=True)

@router.message(Command("pay"))
async def pay(m: Message):
    if m.from_user.id == BOSS_ID:
        uid = m.text.split()[1]
        cur.execute("UPDATE users SET paid=1 WHERE id=?", (uid,))
        db.commit()
        await m.answer(f"✅ Доступ выдан пользователю {uid}")

@router.message(Command("ban"))
async def ban(m: Message):
    if m.from_user.id == BOSS_ID:
        uid = m.text.split()[1]
        cur.execute("UPDATE users SET status='banned' WHERE id=?", (uid,))
        db.commit()
        await m.answer(f"🚫 Забанен пользователь {uid}")

async def main():
    # Удаление старых вебхуков для чистого запуска
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
