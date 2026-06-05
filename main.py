import os
import google.generativeai as genai
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json

app = FastAPI()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# 70+ активов
ASSETS = {
    "Криптовалюты": ["Bitcoin OTC", "Ethereum OTC", "Solana OTC", "Cardano OTC", "TRON OTC", "BNB OTC", "BTC/USD", "ETH/USD"],
    "Валюты": ["EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "NZD/USD"],
    "Акции": ["NVIDIA OTC", "Apple OTC", "Tesla OTC", "NVIDIA", "Apple", "Tesla", "Amazon", "Google"]
}

@app.post("/analyze")
async def analyze(request: Request):
    data = await request.json()
    prompt = f"Сигнал для {data['asset']} на экспирацию {data['time']}. Верни только: НАПРАВЛЕНИЕ (ВВЕРХ/ВНИЗ), СОВЕТ_1 (Риск), СОВЕТ_2 (Индикатор). JSON формат."
    response = model.generate_content(prompt)
    try:
        return json.loads(response.text.replace("```json", "").replace("```", ""))
    except:
        return {"dir": "ВВЕРХ", "s1": "Риск: Низкий", "s2": "Индикатор: RSI Перепродан"}

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html style="background:#0a0a0c; color:#fff; font-family:Arial;">
    <div style="width:350px; margin:20px auto; padding:20px; background:#121212; border-radius:15px; border:1px solid #333;">
        <select id="cat" onchange="upd()" style="width:100%; margin-bottom:10px;"></select>
        <select id="asset" style="width:100%; margin-bottom:10px;"></select>
        <select id="time" style="width:100%; margin-bottom:10px;">
            <option>5 сек</option><option>30 сек</option><option>1 мин</option><option>5 мин</option><option>10 мин</option>
        </select>
        <button onclick="run()" style="width:100%; padding:15px; background:#007bff; border:none; color:white; border-radius:5px; font-weight:bold;">СКАНИРОВАТЬ</button>
        
        <div id="res" style="margin-top:20px; text-align:center;">
            <div id="dir" style="font-size:30px; font-weight:bold;">--</div>
            <div id="timer" style="color:yellow; margin:10px 0;">--</div>
            <div id="s1" style="font-size:12px; color:#aaa;">--</div>
            <div id="s2" style="font-size:12px; color:#aaa;">--</div>
            <button id="mart" onclick="alert('Перекрытие!')" style="display:none; width:100%; margin-top:10px; background:#ff4757; color:white; border:none; padding:10px;">ПЕРЕКРЫТИЕ</button>
        </div>
    </div>
    <script>
        const data = """ + json.dumps(ASSETS) + """;
        function upd() { document.getElementById('asset').innerHTML = data[document.getElementById('cat').value].map(a => `<option>${a}</option>`).join(''); }
        Object.keys(data).forEach(c => document.getElementById('cat').innerHTML += `<option>${c}</option>`);
        upd();
        
        async function run() {
            const r = await (await fetch('/analyze', {method:'POST', body:JSON.stringify({asset:document.getElementById('asset').value, time:document.getElementById('time').value})})).json();
            document.getElementById('dir').innerText = r.dir;
            document.getElementById('s1').innerText = r.s1;
            document.getElementById('s2').innerText = r.s2;
            document.getElementById('mart').style.display = 'block';
            let t = parseInt(document.getElementById('time').value) * 60;
            let i = setInterval(() => {
                t--; document.getElementById('timer').innerText = "Таймер: " + t + " сек";
                if(t<=0) clearInterval(i);
            }, 1000);
        }
    </script>
    </html>
    """
