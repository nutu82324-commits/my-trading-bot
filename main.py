import os
import logging
import time
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

# Настройка профессионального логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Инициализация API
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    logger.critical("API_KEY НЕ УСТАНОВЛЕН В ENV!")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI(title="Team Master AI Terminal")

# CORS для стабильной связи фронта с бэком
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ИНТЕРФЕЙС (HTML/CSS/JS) ---
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TEAM MASTER BOT</title>
    <style>
        :root { --bg: #0b0e14; --panel: #161a21; --accent: #2962ff; --text: #ffffff; --border: #363c4e; }
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { background: var(--panel); width: 100%; max-width: 450px; padding: 25px; border-radius: 16px; border: 1px solid var(--border); box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        h1 { font-size: 20px; text-align: center; margin-bottom: 20px; letter-spacing: 1px; }
        .label { font-size: 11px; color: #888; margin-bottom: 8px; text-transform: uppercase; }
        .grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; margin-bottom: 20px; }
        .box { background: #1e222d; padding: 12px 5px; text-align: center; border: 1px solid var(--border); border-radius: 6px; cursor: pointer; font-size: 11px; transition: 0.2s; }
        .box.active { background: var(--accent); border-color: #fff; transform: scale(1.02); }
        .btn-main { width: 100%; padding: 18px; background: #22c55e; border: none; border-radius: 10px; color: white; font-weight: 800; cursor: pointer; margin-top: 10px; font-size: 14px; }
        #response-area { margin-top: 25px; padding: 15px; background: #000; border-radius: 10px; border-left: 4px solid var(--accent); font-size: 13px; line-height: 1.6; min-height: 100px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>TEAM MASTER BOT</h1>
        <div class="label">ТАЙМФРЕЙМ</div>
        <div class="grid" id="tf-grid">
            <div class="box active" onclick="select(this, 'tf')">S5</div><div class="box" onclick="select(this, 'tf')">M1</div>
            <div class="box" onclick="select(this, 'tf')">M5</div><div class="box" onclick="select(this, 'tf')">M15</div><div class="box" onclick="select(this, 'tf')">H1</div>
        </div>
        <div class="label">СТРАТЕГИЯ</div>
        <div class="grid" id="strat-grid" style="grid-template-columns: repeat(3, 1fr);">
            <div class="box active" onclick="select(this, 'st')">SMC</div><div class="box" onclick="select(this, 'st')">ICT</div><div class="box" onclick="select(this, 'st')">Scalp</div>
        </div>
        <input type="file" id="file-input" style="display:none" accept="image/*">
        <button class="btn-main" onclick="document.getElementById('file-input').click()">🚀 СТАРТ АНАЛИЗА</button>
        <div id="response-area">🤖 Ожидаю загрузку графика...</div>
    </div>
    <script>
        let config = {tf: 'S5', st: 'SMC'};
        function select(el, type) {
            el.parentElement.querySelectorAll('.box').forEach(b => b.classList.remove('active'));
            el.classList.add('active'); config[type] = el.innerText;
        }
        document.getElementById('file-input').onchange = async (e) => {
            const res = document.getElementById('response-area');
            res.innerHTML = "⏳ Анализирую " + config.tf + " по " + config.st + "...";
            const fd = new FormData();
            fd.append('file', e.target.files[0]); fd.append('tf', config.tf); fd.append('st', config.st);
            try {
                const response = await fetch('/analyze', {method: 'POST', body: fd});
                const data = await response.json();
                res.innerHTML = data.result.replace(/\\n/g, '<br>');
            } catch(err) { res.innerHTML = "❌ Ошибка соединения: " + err.message; }
        };
    </script>
</body>
</html>
"""

@app.get("/")
async def root(): return HTMLResponse(HTML_INTERFACE)

@app.post("/analyze")
async def analyze_trade(file: UploadFile = File(...), tf: str = Form(...), st: str = Form(...)):
    start_time = time.time()
    try:
        logger.info(f"Начало анализа: TF={tf}, Strategy={st}")
        img_bytes = await file.read()
        
        # Глубокий промпт для ИИ
        prompt = f"""
        Ты профессиональный трейдер-наставник. Проанализируй этот график.
        Параметры: Таймфрейм {tf}, Стратегия {st}.
        
        Твоя задача:
        1. ВЕРДИКТ: Жирный BUY или SELL со смайлом (🟢/🔴).
        2. АНАЛИЗ: Обоснуй вход (ликвидность, дисбалансы, слом структуры).
        3. РИСК-МЕНЕДЖМЕНТ: Точные уровни Stop Loss и Take Profit.
        4. ЭКСПИРАЦИЯ: Время сделки в минутах.
        5. СОВЕТ: Короткий дерзкий совет трейдеру.
        """
        
        response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": img_bytes}])
        
        logger.info(f"Анализ завершен за {time.time() - start_time:.2f} сек")
        return {"result": response.text}
        
    except Exception as e:
        logger.error(f"КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка при обработке ИИ")

