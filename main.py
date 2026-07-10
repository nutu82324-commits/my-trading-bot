import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
import google.generativeai as genai

app = FastAPI()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

HTML_UI = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background: #0b0e14; color: #fff; font-family: sans-serif; padding: 10px; }
        .panel { background: #161a21; border-radius: 12px; border: 1px solid #363c4e; max-width: 450px; margin: auto; padding: 20px; }
        .grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; margin: 10px 0; }
        .box { background: #1e222d; padding: 10px; text-align: center; border: 1px solid #363c4e; border-radius: 4px; cursor: pointer; font-size: 10px; }
        .box.active { background: #2962ff; border-color: #fff; }
        .strat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px; margin: 15px 0; }
        .btn-action { width: 100%; padding: 15px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; color: white; margin-top: 10px; }
        #res { margin-top: 20px; padding: 15px; background: #000; border-radius: 8px; border-left: 4px solid #22c55e; line-height: 1.5; }
    </style>
</head>
<body>
    <div class="panel">
        <h2 style="text-align:center;">TEAM MASTER BOT</h2>
        <div style="font-size:12px; color:#888;">ИНТЕРВАЛ</div>
        <div class="grid" id="tfs">
            <div class="box active" onclick="sel(this,'tf')">S5</div><div class="box" onclick="sel(this,'tf')">M1</div><div class="box" onclick="sel(this,'tf')">M5</div><div class="box" onclick="sel(this,'tf')">M15</div><div class="box" onclick="sel(this,'tf')">H1</div>
        </div>
        <div style="font-size:12px; color:#888;">СТРАТЕГИЯ</div>
        <div class="strat-grid" id="strats">
            <div class="box active" onclick="sel(this,'st')">SMC</div><div class="box" onclick="sel(this,'st')">ICT</div><div class="box" onclick="sel(this,'st')">Scalp</div>
        </div>
        <input type="file" id="f" style="display:none" accept="image/*">
        <button class="btn-action" style="background:#22c55e" onclick="document.getElementById('f').click()">СТАРТ АНАЛИЗА</button>
        <div id="res">🤖 Бот готов. Загрузи график для получения сигнала.</div>
    </div>
    <script>
        let state = {tf: 'S5', st: 'SMC'};
        function sel(el, type) { el.parentElement.querySelectorAll('.box').forEach(b => b.classList.remove('active')); el.classList.add('active'); state[type] = el.innerText; }
        document.getElementById('f').onchange = async (e) => {
            document.getElementById('res').innerText = "⏳ Анализирую " + state.tf + " по " + state.st + "...";
            const fd = new FormData(); fd.append('file', e.target.files[0]); fd.append('tf', state.tf); fd.append('st', state.st);
            const r = await fetch('/analyze', {method:'POST', body:fd});
            const d = await r.json();
            document.getElementById('res').innerHTML = d.result.replace(/\\n/g, '<br>');
        };
    </script>
</body>
</html>
"""

@app.get("/")
def get(): return HTMLResponse(HTML_UI)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...), tf: str = Form(...), st: str = Form(...)):
    img_data = await file.read()
    prompt = f"""Ты — профи трейдер. Анализируй график (Таймфрейм: {tf}, Стратегия: {st}).
    1. Вердикт: BUY или SELL (жирный смайл 🟢 или 🔴).
    2. Почему: четкий разбор ликвидности/блоков.
    3. Риск-менеджмент: уровень Стоп-Лосс и Тейк-Профит.
    4. Отсчет: время до конца свечи (если есть на скрине) или общая рекомендация по экспирации.
    Будь дерзким, отвечай как наставник."""
    response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": img_data}])
    return {"result": response.text}
