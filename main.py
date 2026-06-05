import os
import json
import google.generativeai as genai
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

ASSETS = {
    "Криптовалюты": ["Bitcoin OTC", "Ethereum OTC", "Solana OTC", "BTC/USD", "ETH/USD"],
    "Валюты": ["EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "EUR/USD", "GBP/USD"],
    "Акции": ["NVIDIA OTC", "Apple OTC", "Tesla OTC", "Amazon"]
}

@app.post("/analyze")
async def analyze(request: Request):
    try:
        data = await request.json()
        prompt = f"Торговый сигнал для {data['asset']} на {data['time']}. Верни ТОЛЬКО прогноз (ВВЕРХ/ВНИЗ) и процент точности."
        response = model.generate_content(prompt)
        return {"res": response.text}
    except: return {"res": "Ошибка API"}

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html style="background:#050505; color:#fff; font-family:sans-serif;">
    <div id="widget" style="width:320px; margin:20px auto; padding:15px; background:#1a1a1a; border-radius:15px; border:1px solid #333;">
        <div style="text-align:center; font-weight:bold; margin-bottom:10px;">QUANTUM CORE v5</div>
        <select id="cat" onchange="upd()" style="width:100%; background:#000; color:#fff; margin-bottom:5px;"></select>
        <select id="asset" style="width:100%; background:#000; color:#fff; margin-bottom:5px;"></select>
        <select id="time" style="width:100%; background:#000; color:#fff; margin-bottom:15px;">
            <option>5 сек</option><option>30 сек</option><option>1 мин</option><option>5 мин</option>
        </select>
        <div style="display:flex; justify-content:space-between; margin-bottom:15px;">
            <div onclick="add(1)" style="background:#00ff88; padding:10px; border-radius:5px; cursor:pointer;">WIN: <span id="w">0</span></div>
            <div onclick="add(0)" style="background:#ff4757; padding:10px; border-radius:5px; cursor:pointer;">LOSS: <span id="l">0</span></div>
        </div>
        <button onclick="run()" style="width:100%; padding:15px; background:#007bff; border:none; color:white; font-weight:bold;">АНАЛИЗ</button>
        <div id="out" style="margin-top:15px; text-align:center; font-size:18px;">Жду старт...</div>
    </div>
    <script>
        const d = """ + json.dumps(ASSETS) + """;
        let w=0, l=0;
        function upd(){ document.getElementById('asset').innerHTML = d[document.getElementById('cat').value].map(a => `<option>${a}</option>`).join(''); }
        function add(isW){ isW?w++:l++; document.getElementById('w').innerText=w; document.getElementById('l').innerText=l; }
        Object.keys(d).forEach(c => document.getElementById('cat').innerHTML += `<option>${c}</option>`);
        upd();
        async function run(){
            document.getElementById('out').innerText = "Анализирую...";
            let r = await (await fetch('/analyze', {method:'POST', body:JSON.stringify({asset:document.getElementById('asset').value, time:document.getElementById('time').value})})).json();
            document.getElementById('out').innerText = r.res;
        }
    </script>
    </html>
    """
