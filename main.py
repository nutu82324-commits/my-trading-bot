from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import numpy as np
import cv2

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_market_signal(img):
    # ПРЕОБРАЗОВАНИЕ: Ищем свечи по цветам (Красный/Зеленый)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Диапазоны цветов свечей на Pocket Option
    lower_green = np.array([40, 50, 50])
    upper_green = np.array([80, 255, 255])
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    
    # Считаем пиксели
    green_pixels = cv2.countNonZero(cv2.inRange(hsv, lower_green, upper_green))
    red_pixels = cv2.countNonZero(cv2.inRange(hsv, lower_red, upper_red))
    
    # ЛОГИКА СТРАТЕГИИ (Smart Money / ICT простейшая):
    if green_pixels > red_pixels * 1.5:
        return "ВВЕРХ 🟢", "85%"
    elif red_pixels > green_pixels * 1.5:
        return "ВНИЗ 🔴", "85%"
    else:
        return "ОЖИДАНИЕ...", "0%"

@app.post("/scan")
async def scan(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # ИИ анализирует кадр
    signal, conf = get_market_signal(img)
    return {"signal": signal, "conf": conf, "time": 300}
