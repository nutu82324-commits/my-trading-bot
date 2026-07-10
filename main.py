import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import google.generativeai as genai

app = FastAPI()
# Ключ берется из настроек Render (раздел Environment)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

HTML_UI = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background: #0b0e14; color: #fff; font-family: sans-serif; display: flex; justify-content: center; padding: 20px; }
        .panel { background: #161a21; padding: 20px; border-radius: 12px; width: 450px; border: 1px solid #363c4e; }
        .grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; margin-top: 10px; }
        .box { background: #1e222d; padding: 10px; text-align: center; border-radius: 4px; border: 1px solid #363c4e; font-size: 10px; cursor: pointer; }
        .strat { background: #1e222d; padding: 12px; margin-top: 10px; border-radius: 4px; border: 1px solid #363c4e; text-align: center; }
        .btn { width: 100%; padding: 15px; border: none; border-radius: 8px; color: white; font-weight: bold; cursor: pointer; margin-top: 10px; }
        #res { margin-top: 20px; padding: 15px; background: #0b0e14; border-radius: 8px; border-left: 4px solid #2962ff; font-size: 14px; }
    </style>
</head>
<body>
    <div class="panel">
        <h2 style="text-align:center; font-size:16px;">MASTER AI TERMINAL</h2>
        <div class="grid">
            <div class="box">S5</div><div class="box">S15</div><div class="box">M1</div><div class="box">M5</div><div class="box">M15</div>
        </div>
        <div class="strat">Стратегия: <b>Smart Money (SMC)</b></div>
        <input type="file" id="f" style="display:none" accept="image/*">
        <button class="btn" style="background:#2962ff" onclick="document.getElementById('f').click()">ДОБАВИТЬ СКРИН</button>
        <button class="btn" style="background:#0891b2" onclick="alert('Камера Live включена')">КАМЕРА LIVE</button>
        <div id="res">Сигнал: готов к работе...</div>
    </div>
    <script>
        document.getElementById('f').onchange = async (e) => {
            document.getElementById('res').innerText = "Анализирую ликвидность и FVG...";
            const fd = new FormData();
            fd.append('file', e.target.files[0]);
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
async def analyze(file: UploadFile = File(...)):
    img_data = await file.read()
    # Вот тут зашита логика для твоей проходимости
    prompt = """
    Ты — эксперт-трейдер SMC/ICT. Твоя задача: повысить проходимость сделок.
    1. Анализ: Ликвидность, OB (Order Blocks), FVG (Imbalance).
    2. Вывод: BUY или SELL 🟢/🔴.
    3. Обоснование: Почему этот сигнал сильный.
    4. Риск: Тейк-профит и Стоп-лосс уровни.
    Будь максимально строгим, если паттерн слабый — пиши "ВНЕ РЫНКА".
    """
    response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": img_data}])
    return {"result": response.text}
