from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import numpy as np
import cv2

app = FastAPI()

# --- CSS И ДИЗАЙН ---
UI_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { background: #0c0e12; color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 15px; }
        .glass-panel { background: #1a1d24; border-radius: 20px; padding: 20px; border: 1px solid #333; }
        video { width: 100%; border-radius: 15px; border: 2px solid #5d3fd3; }
        .btn-scan { background: linear-gradient(135deg, #6c5ce7, #a29bfe); border: none; padding: 20px; width: 100%; border-radius: 15px; color: white; font-weight: bold; font-size: 18px; margin-top: 15px; }
        #timer { font-size: 48px; color: #00ff88; font-weight: bold; margin: 15px 0; }
        .status-box { margin-top: 20px; padding: 15px; border-left: 4px solid #6c5ce7; background: #222; }
    </style>
</head>
<body>
    <div class="glass-panel">
        <video id="v" autoplay playsinline></video>
        <button class="btn-scan" onclick="scan()">СКАНИРОВАТЬ РЫНОК</button>
        <div id="timer">00:00</div>
        <div class="status-box" id="res">ОЖИДАНИЕ СИГНАЛА...</div>
    </div>
    <script>
        const v = document.getElementById('v');
        navigator.mediaDevices.getUserMedia({video: {facingMode: "environment"}}).then(s => v.srcObject = s);
        async function scan() {
            const canvas = document.createElement('canvas');
            canvas.width = v.videoWidth; canvas.height = v.videoHeight;
            canvas.getContext('2d').drawImage(v, 0, 0);
            const blob = await new Promise(r => canvas.toBlob(r, 'image/jpeg'));
            const fd = new FormData(); fd.append('file', blob);
            const r = await fetch('/scan', {method: 'POST', body: fd});
            const d = await r.json();
            document.getElementById('res').innerHTML = "СИГНАЛ: " + d.signal + "<br>ОБОСНОВАНИЕ: " + d.reason;
            startTimer(d.time);
        }
        function startTimer(s) {
            let t = s;
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
async def index():
    return UI_HTML

@app.post("/scan")
async def scan(file: UploadFile = File(...)):
    # --- ЛОГИКА ИИ (Анализ контраста) ---
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Имитируем анализ: если средняя яркость в центре выше 120, даем сигнал
    avg = np.mean(gray)
    if avg > 120:
        return {"signal": "ВВЕРХ 🟢", "reason": "Smart Money: Имбаланс обнаружен", "time": 300}
    else:
        return {"signal": "ВНИЗ 🔴", "reason": "ICT: Слом структуры (BOS)", "time": 300}
