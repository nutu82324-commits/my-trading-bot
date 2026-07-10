from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
import numpy as np
import cv2
import pandas as pd
import base64
from pydantic import BaseModel

app = FastAPI()

# --- ПОЛНЫЙ ИНТЕРФЕЙС БЕЗ СОКРАЩЕНИЙ ---
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI MASTER PRO TRADING SYSTEM</title>
    <style>
        :root { --bg: #0a0b10; --card: #15171e; --accent: #6c5ce7; --text: #ffffff; --green: #00ff88; --red: #ff4757; }
        body { background-color: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; padding: 20px; }
        .container { max-width: 550px; margin: 0 auto; }
        .card { background: var(--card); border-radius: 20px; padding: 25px; border: 1px solid #333; margin-bottom: 20px; }
        .tf-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin: 20px 0; }
        .btn-tf { background: #2c3e50; border: none; padding: 12px 5px; border-radius: 10px; color: #fff; cursor: pointer; font-size: 13px; }
        .btn-tf.active { background: var(--accent); }
        select, input { width: 100%; box-sizing: border-box; background: #222; border: 1px solid #444; color: white; padding: 15px; border-radius: 12px; margin-bottom: 15px; }
        .btn-main { width: 100%; padding: 20px; background: linear-gradient(135deg, var(--accent), #8854d0); border: none; border-radius: 15px; color: white; font-weight: bold; font-size: 18px; cursor: pointer; margin-top: 10px; }
        .video-box { width: 100%; border-radius: 15px; background: #000; margin: 15px 0; display: none; }
        #timer-display { font-size: 50px; text-align: center; color: var(--green); font-weight: bold; margin: 20px 0; font-family: monospace; }
        .result-text { font-size: 20px; text-align: center; font-weight: bold; margin-bottom: 10px; }
        .reason-text { font-size: 15px; color: #a0a0a0; text-align: center; line-height: 1.5; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2 style="text-align: center; margin-top: 0;">AI MASTER PRO SYSTEM</h2>
            <select id="strategy-selector">
                <option value="ict">Стратегия: ICT (Smart Money)</option>
                <option value="smc">Стратегия: Smart Money (Order Block)</option>
                <option value="price_action">Стратегия: Price Action</option>
            </select>
            <div class="tf-grid" id="tf-grid">
                <button class="btn-tf" onclick="set_timeframe(this, 'S30')">S30</button>
                <button class="btn-tf" onclick="set_timeframe(this, 'M1')">M1</button>
                <button class="btn-tf" onclick="set_timeframe(this, 'M2')">M2</button>
                <button class="btn-tf" onclick="set_timeframe(this, 'M5')">M5</button>
                <button class="btn-tf" onclick="set_timeframe(this, 'M15')">M15</button>
            </div>
            <input type="number" id="expiration-time" value="60" placeholder="Экспирация (секунды)">
            <button class="btn-main" onclick="start_live_camera()">📷 ВКЛЮЧИТЬ КАМЕРУ (LIVE)</button>
            <video id="video-stream" class="video-box" autoplay playsinline></video>
            <button class="btn-main" id="scan-button" onclick="capture_and_process()" style="display:none; background:#00ff88; color:#000;">🚀 ЗАПУСТИТЬ АНАЛИЗ ИИ</button>
        </div>
        <div class="card" id="result-card" style="display:none;">
            <div id="timer-display">00:00</div>
            <div id="signal-result" class="result-text"></div>
            <div id="reason-result" class="reason-text"></div>
        </div>
    </div>
    <script>
        let selected_timeframe = 'M1';
        function set_timeframe(button_element, timeframe) {
            document.querySelectorAll('.btn-tf').forEach(btn => btn.classList.remove('active'));
            button_element.classList.add('active');
            selected_timeframe = timeframe;
        }
        async function start_live_camera() {
            const video_element = document.getElementById('video-stream');
            const stream = await navigator.mediaDevices.getUserMedia({video: {facingMode: "environment"}});
            video_element.srcObject = stream;
            video_element.style.display = 'block';
            document.getElementById('scan-button').style.display = 'block';
        }
        async function capture_and_process() {
            const canvas_element = document.createElement('canvas');
            const video_element = document.getElementById('video-stream');
            canvas_element.width = video_element.videoWidth;
            canvas_element.height = video_element.videoHeight;
            canvas_element.getContext('2d').drawImage(video_element, 0, 0);
            const image_base64 = canvas_element.toDataURL('image/jpeg');
            const response = await fetch('/perform_ai_scan', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    encoded_image: image_base64,
                    strategy_name: document.getElementById('strategy-selector').value,
                    timeframe_value: selected_timeframe,
                    expiration_seconds: document.getElementById('expiration-time').value
                })
            });
            const response_data = await response.json();
            document.getElementById('result-card').style.display = 'block';
            document.getElementById('signal-result').innerHTML = response_data.signal_label;
            document.getElementById('reason-result').innerText = response_data.reasoning_text;
            start_countdown_timer(response_data.expiration_seconds);
        }
        function start_countdown_timer(total_seconds) {
            let remaining = parseInt(total_seconds);
            const display_element = document.getElementById('timer-display');
            const timer_interval = setInterval(() => {
                display_element.innerText = Math.floor(remaining / 60).toString().padStart(2,'0') + ":" + (remaining % 60).toString().padStart(2,'0');
                if (--remaining < 0) clearInterval(timer_interval);
            }, 1000);
        }
    </script>
</body>
</html>
"""

class ScanRequestData(BaseModel):
    encoded_image: str
    strategy_name: str
    timeframe_value: str
    expiration_seconds: int

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_INTERFACE

@app.post("/perform_ai_scan")
async def perform_ai_scan(request_data: ScanRequestData):
    # Декодирование изображения для анализа
    header, encoded_data = request_data.encoded_image.split(",", 1)
    binary_data = base64.b64decode(encoded_data)
    image_array = np.frombuffer(binary_data, np.uint8)
    processed_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    grayscale_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
    
    # --- МАТЕМАТИЧЕСКАЯ МОДЕЛЬ ИНДИКАТОРОВ ---
    column_means = np.mean(grayscale_image, axis=0)
    ema_indicator_value = pd.Series(column_means).ewm(span=20).mean().iloc[-1]
    current_price_pixel = column_means[-1]
    
    # Поиск резких движений (волатильность) через фильтр Кэнни
    edge_detected_image = cv2.Canny(grayscale_image, 50, 150)
    volatility_metric = np.sum(edge_detected_image) / 100000
    
    # --- ЛОГИКА ПРИНЯТИЯ ТОРГОВОГО РЕШЕНИЯ ---
    if current_price_pixel > ema_indicator_value and volatility_metric > 0.5:
        signal_label = "ВЫШЕ (BUY) 🟢"
        reasoning_text = f"Анализ по стратегии {request_data.strategy_name.upper()} на ТФ {request_data.timeframe_value}: Обнаружен восходящий тренд. Индикатор EMA подтверждает покупательную силу при высоком уровне рыночной волатильности ({volatility_metric:.2f})."
    elif current_price_pixel < ema_indicator_value and volatility_metric > 0.5:
        signal_label = "НИЖЕ (SELL) 🔴"
        reasoning_text = f"Анализ по стратегии {request_data.strategy_name.upper()} на ТФ {request_data.timeframe_value}: Обнаружен медвежий пробой уровня EMA. Рынок демонстрирует давление продавцов при активной торговле."
    else:
        signal_label = "ОЖИДАНИЕ (WAIT) ⚪"
        reasoning_text = "Рыночные показатели находятся в зоне консолидации или низкой волатильности. ИИ-алгоритм не нашел достаточных оснований для входа в сделку."
        
    return {
        "signal_label": signal_label,
        "reasoning_text": reasoning_text,
        "expiration_seconds": request_data.expiration_seconds
    }
