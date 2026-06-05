import os
import json
import google.generativeai as genai
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# 70+ активов разделены по категориям
ASSETS = {
    "Валюты": ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "EUR/JPY", "USD/CAD", "GBP/JPY", "NZD/USD", "USD/CHF", "EUR/GBP"],
    "Крипто": ["BTC/USD", "ETH/USD", "SOL/USD", "ADA/USD", "DOT/USD", "XRP/USD", "LTC/USD", "BNB/USD", "TRX/USD", "DOGE/USD"],
    "Акции": ["AAPL", "TSLA", "NVDA", "AMZN", "GOOGL", "MSFT", "META", "NFLX", "AMD", "INTC"]
}

@app.post("/analyze")
async def analyze(request: Request):
    data = await request.json()
    # Запрос к ИИ
    prompt = f"Дай торговый сигнал для {data['asset']} на {data['time']}. Верни только направление (ВВЕРХ/ВНИЗ) и точность."
    response = model.generate_content(prompt)
    return {"signal": response.text}

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html style="background:#0a0a0c; color:#fff; font-family:sans-serif;">
    <style>
        .box { width:320px; margin:20px auto; padding:20px; background:#121212; border:1px solid #333; border-radius:15px; text-align:center; }
        select, button { width:100%; padding:10px; margin:5px 0; background:#222; color:#fff; border:1px solid #444; border-radius:5px; }
        #res { font-size:24px; font-weight:bold; margin:15px 0; }
        #timer { font-size:18px; color:#ffcc00; }
    </style>
    <div class="box">
        <h3>QUANTUM CORE v4.2</h3>
        <select id="cat" onchange="upd()"></select>
        <select id="asset"></select>
        <select id="time">
            <option>5 сек</option><option>15 сек</option><option>30 сек</option><option>1 мин</option>
            <option>2 мин</option><option>3 мин</option><option>4 мин</option><option>5 мин</option>
        </select>
        <button onclick="run()" style="background:#007bff; font-weight:bold;">ЗАПУСК АНАЛИЗА</button>
        <div id="res">--</div>
        <div id="timer"></div>
        <button id="mart" onclick="alert('Перекрытие!')" style="display:none; background:#ff4757;">ПЕРЕКРЫТИЕ</button>
    </div>
    <script>
        const data = """ + json.dumps(ASSETS) + """;
        function upd(){ let c=document.getElementById('cat').value; document.getElementById('asset').innerHTML = data[c].map(a => `<option>${a}</option>`).join(''); }
        Object.keys(data).forEach(c => document.getElementById('cat').innerHTML += `<option>${c}</option>`);
        upd();
        async function run(){
            document.getElementById('res').innerText = "Анализ...";
            let r = await (await fetch('/analyze', {method:'POST', body:JSON.stringify({asset:document.getElementById('asset').value, time:document.getElementById('time').value})})).json();
            document.getElementById('res').innerText = r.signal;
            document.getElementById('mart').style.display = 'block';
            let t = parseInt(document.getElementById('time').value) * (document.getElementById('time').value.includes('сек')?1:60);
            let i = setInterval(()=>{ t--; document.getElementById('timer').innerText = "Таймер: " + t + " сек"; if(t<=0) clearInterval(i); }, 1000);
        }
    </script>
    </html>
    """
