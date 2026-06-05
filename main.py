import pyautogui
import google.generativeai as genai
import keyboard
import time

# Настрой свой ключ
genai.configure(api_key="ТВОЙ_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')

def scan_screen():
    print("Делаю скриншот графика...")
    screenshot = pyautogui.screenshot()
    screenshot.save("graph.png")
    
    with open("graph.png", "rb") as file:
        img_data = file.read()
        
    response = model.generate_content([
        "Проанализируй график на картинке. Дай сигнал ВВЕРХ или ВНИЗ, точность и совет.",
        {"mime_type": "image/png", "data": img_data}
    ])
    print(f"СИГНАЛ: {response.text}")

print("Нажми F9, чтобы сканировать график...")
keyboard.add_hotkey('f9', scan_screen)
keyboard.wait()
