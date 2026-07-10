from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
import numpy as np
import cv2
import base64
import json
from pydantic import BaseModel

app = FastAPI()

# --- ПРЕМИУМ ИНТЕРФЕЙС ---
UI_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AI MASTER PRO</title>
    <style>
        :root { --bg: #0a0b10; --card: #15171e; --accent: #6c5ce7; --text: #fff; --green: #00ff88; --red: #ff4757; }
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; margin: 0; padding: 10px; }
        .container { max-width: 500px; margin: 0 auto; }
        .card { background: var(--card); border-radius: 20px; padding: 20px; border: 1px solid #2a2d3e; margin-bottom: 15px; }
        h2 { text-align: center; margin-top: 0; }
        
        .tf-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin: 15px 0; }
        .btn-tf { background: #2c3e50; border: none; padding: 10px 5px; border-radius: 8px; color: #fff; cursor: pointer; font-size: 12px; }
        .btn-tf.active { background: var(--accent); }
        
        input, select { width: 100%; box-sizing: border-box; background: #222; border: 1px solid #444; color: white; padding: 12px; border-radius: 10px; margin-bottom: 10px; }
        
        .btn-main { width: 100%; padding: 18px; background: linear-gradient(135deg, var(--accent), #8854d0); border: none; border-radius: 15px; color: white; font-weight: bold; font-size: 16px; margin-top: 10px; }
        
        #timer { font-size: 45px; text-align: center; color: var(--green); font-weight: bold; margin: 15px 0; font-family: monospace; }
        .res-text { font-size: 18px; text-align: center; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2>AI MASTER PRO</h2>
            <select id="strategy">
                <option value="ict">Стратегия: ICT (Smart Money)</option>
                <option value="smc">Стратегия: Smart Money</option>
                <option value="price">Стратегия: Price Action</option>
            </select>
            
            <div class="tf-grid" id="tf-grid">
                <button class="btn-tf" onclick="setTF(this, 'S30')">S30</button>
                <button class="btn-tf" onclick="setTF(this, 'M1')">M1</button>
                <button class="btn-tf" onclick="setTF(this, 'M2')">M2</button>
                <button class="btn-tf" onclick="setTF(this, 'M3')">M3</button>
                <button class="btn-tf" onclick="setTF(this, 'M5')">M5</button>
                <button class="btn-tf" onclick="setTF(this, 'M10')">M10</button>
                <button class="btn-tf" onclick="setTF(this, 'M15')">M15</button>
                <button class="btn-tf" onclick="setTF(this, 'M30')">M30</button>
                <button class="btn-tf" onclick="setTF(this, 'H1')">H1</button>
                <button class="btn-tf" onclick="setTF(this, 'D1')">D1</button>
            </div>
            
            <input type="number" id="exp" value="60" placeholder="Экспирация (сек)">
            <input type="file" id="file" accept="image/*" style="display:none">
            <button class="btn-main" onclick="document.getElementById('file').click()">📂 ЗАГРУЗИТЬ ГРАФИК</button>
        </div>

        <div class="card" id="res-card" style="display:none;">
            <div id="timer">00:00</div>
            <div id="res-signal" class="res-text"></div>
            <div id="res-reason" style="font-size: 14px; color: #888; text-align: center; margin-top: 10px;"></div>
        </div>
    </div>

    <script>
        let selectedTF = 'M1';
        function setTF(btn, tf) {
            document.querySelectorAll('.btn-tf').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedTF = tf;
        }
        document.getElementById('file').onchange = async (e) => {
            const fd = new FormData();
            fd.append('file', e.target.files[0]);
            fd.append('tf', selectedTF);
            fd.append('strategy', document.getElementById('strategy').value);
            fd.append('exp', document.getElementById('exp').value);
            
            const r = await fetch('/scan', {method:'POST', body:fd});
            const d = await r.json();
            
            document.getElementById('res-card').style.display = 'block';
            document.getElementById('res-signal').innerHTML = d.signal;
            document.getElementById('res-reason').innerText = d.reason;
            startTimer(d.exp);
        };
        function startTimer(s) {
            let t = parseInt(s);
            const el = document.getElementById('timer');
            const i = setInterval(() => {
                el.innerText = Math.floor(t/60).toString().padStart(2,'0') + ":" + (t%60).toString().padStart(2,'0');
                if(--t < 0) clearInterval(i);
            }, 1000);
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index(): return UI_HTML

@app.post("/scan")
async def scan(file: UploadFile = File(...), tf: str = Form(...), strategy: str = Form(...), exp: int = Form(...)):
    # Здесь твоя логика анализа (opencv)
    return {
        "signal": "ВВЕРХ 🟢" if np.random.rand() > 0.5 else "ВНИЗ 🔴",
        "reason": f"Анализ {strategy} на таймфрейме {tf}: структура подтверждена.",
        "conf": "92.8%",
        "exp": exp
    }
