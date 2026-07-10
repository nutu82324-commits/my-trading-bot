import os
import json
import logging
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
import google.generativeai as genai

# Настройка логирования для стабильной работы на эфире
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TeamMasterBot")

app = FastAPI()

# Инициализация ИИ
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    logger.error("GEMINI_API_KEY не найден в окружении!")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Весь интерфейс с версткой 1:1 как на твоем фото
HTML_UI = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TEAM MASTER BOT</title>
    <style>
        body { background: #0b0e14; color: #a1a6b3; font-family: 'Segoe UI', sans-serif; padding: 20px; margin: 0; }
        .main-panel { background: #161a21; max-width: 600px; margin: auto; padding: 25px; border-radius: 12px; border: 1px solid #363c4e; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .status-badge { background: #1e222d; padding: 5px 12px; border-radius: 4px; font-size: 11px; color: #ff4d4d; border: 1px solid #363c4e; }
        .label { color: #fff; font-size: 13px; margin-bottom: 12px; font-weight: bold; text-transform: uppercase; }
        .grid-int { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-bottom: 20px; }
        .box { background: #1e222d; padding: 12px 5px; text-align: center; border: 1px solid #363c4e; border-radius: 4px; cursor: pointer; font-size: 11px; color: #fff; transition: 0.2s; }
        .box.active { border-color: #5b6683; background: #2a2e39; color: #2962ff; }
        .exp-container { display: flex; align-items: center; justify-content: space-between; background: #1e222d; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #363c4e; }
        .exp-val { font-size: 20px; font-weight: bold; color: #fff; }
        .strat-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 25px; }
        .strat-card { background: #1e222d; padding: 15px 8px; border: 1px solid #363c4e; border-radius: 8px; text-align: center; cursor: pointer; font-size: 10px; color: #a1a6b3; }
        .strat-card.active { border-color: #2962ff; color: #fff; background: #1a2030; }
        .btn-row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .btn { padding: 18px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; color: white; }
        #response-area { margin-top: 25px; padding: 20px; background: #0b0e14; border-radius: 8px; font-size: 14px; color: #e0e0e0; border-left: 4px solid #2962ff; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="main-panel">
        <div class="header">
            <div style="font-weight:bold; color:white;">TEAM MASTER</div>
            <div class="status-badge" id="status">● БОТ ОСТАНОВЛЕН</div>
        </div>
        
        <div class="label">ИНТЕРВАЛ</div>
        <div class="grid-int" id="int-grid">
            <script>
                ['S5','S10','S15','S30','M1','M2','M3','M5','M10','M15','M30','H1','H4','D1'].forEach(t => {
                    document.write(`<div class="box ${t=='M2'?'active':''}" onclick="select(this,'int')">${t}</div>`);
                });
            </script>
        </div>

        <div class="label">ЭКСПИРАЦИЯ</div>
        <div class="exp-container">
            <button onclick="changeExp(-1)">–</button>
            <div class="exp-val" id="exp-val">5</div>
            <button onclick="changeExp(1)">+</button>
            <span style="font-size:12px;">МИН</span>
        </div>

        <div class="label">СТРАТЕГИИ</div>
        <div class="strat-grid" id="strat-grid">
            <div class="strat-card active" onclick="select(this,'strat')">Smart Money</div>
            <div class="strat-card" onclick="select(this,'strat')">ICT</div>
            <div class="strat-card" onclick="select(this,'strat')">Price Action</div>
            <div class="strat-card" onclick="select(this,'strat')">Scalping</div>
            <div class="strat-card" onclick="select(this,'strat')">Trend Following</div>
        </div>

        <input type="file" id="file-input" style="display:none" accept="image/*">
        <div class="btn-row">
            <button class="btn" style="background:#22c55e" onclick="startAnalysis()">СТАРТ</button>
            <button class="btn" style="background:#ef4444" onclick="location.reload()">СТОП</button>
        </div>
        <div id="response-area">🤖 Ожидание анализа...</div>
    </div>

    <script>
        let cfg = {int: 'M2', strat: 'Smart Money', exp: 5};
        function select(el, type) {
            el.parentElement.querySelectorAll('.box, .strat-card').forEach(b => b.classList.remove('active'));
            el.classList.add('active');
            cfg[type] = el.innerText;
        }
        function changeExp(v) { 
            cfg.exp = Math.max(1, cfg.exp + v); 
            document.getElementById('exp-val').innerText = cfg.exp; 
        }
        function startAnalysis() {
            document.getElementById('file-input').click();
        }
        document.getElementById('file-input').onchange = async (e) => {
            const res = document.getElementById('response-area');
            res.innerHTML = "⏳ Анализирую график... Пожалуйста, подождите.";
            document.getElementById('status').innerText = "● АНАЛИЗ В ХОДЕ...";
            const fd = new FormData();
            fd.append('file', e.target.files[0]);
            fd.append('cfg', JSON.stringify(cfg));
            try {
                const r = await fetch('/analyze', {method: 'POST', body: fd});
                const data = await r.json();
                res.innerHTML = data.result.replace(/\\n/g, '<br>');
                document.getElementById('status').innerText = "● БОТ ОЖИДАЕТ";
            } catch(err) { res.innerText = "❌ Ошибка сети."; }
        };
    </script>
</body>
</html>
"""

@app.get("/")
async def get_ui(): return HTMLResponse(HTML_UI)

@app.post("/analyze")
async def analyze_chart(file: UploadFile = File(...), cfg: str = Form(...)):
    try:
        config = json.loads(cfg)
        img_bytes = await file.read()
        prompt = f"""
        Ты — профессиональный трейдер Team Master. 
        Анализируй этот график (Таймфрейм: {config['int']}, Стратегия: {config['strat']}, Экспирация: {config['exp']} мин).
        Твой ответ:
        1. ВЕРДИКТ: 🟢BUY или 🔴SELL.
        2. АНАЛИЗ: Почему (ликвидность, структура).
        3. СТОП/ТЕЙК: Уровни.
        4. СОВЕТ: Действуй профессионально.
        """
        response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": img_bytes}])
        return {"result": response.text}
    except Exception as e:
        logger.error(f"AI Error: {e}")
        return {"result": "❌ Ошибка ИИ. Проверь API ключ и лимиты."}
