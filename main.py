from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import cv2
import numpy as np

app = FastAPI()

# Логика анализа графиков
def analyze_patterns(image):
    # Преобразуем в оттенки серого для анализа
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # ПРИМЕР: Поиск зон через границы (Canny)
    edges = cv2.Canny(gray, 50, 150)
    
    # Здесь добавляется твоя логика стратегий:
    # 1. Поиск FVG (Fair Value Gap)
    # 2. Поиск Order Block
    # 3. Расчет волатильности
    
    # Заглушка для теста
    return {"signal": "BUY (Smart Money)", "confidence": "78%", "level": "1.0850"}

@app.post("/api/scan")
async def scan(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    result = analyze_patterns(img)
    return result

app.mount("/", StaticFiles(directory="static", html=True), name="static")
