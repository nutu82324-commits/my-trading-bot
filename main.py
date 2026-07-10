from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import numpy as np
import cv2
import os

app = FastAPI()

# Указываем, где лежат шаблоны
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/scan")
async def scan(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Логика анализа (HSV - поиск цвета свечей)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(hsv, (40, 50, 50), (90, 255, 255))
    red_mask = cv2.inRange(hsv, (0, 100, 100), (10, 255, 255))
    
    green_count = cv2.countNonZero(green_mask)
    red_count = cv2.countNonZero(red_mask)
    
    if green_count > red_count:
        signal = "ВВЕРХ 🟢"
    else:
        signal = "ВНИЗ 🔴"
        
    return {"signal": signal, "conf": "85%", "time": 300}
