import sys
import pyautogui
import google.generativeai as genai
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QComboBox, QGridLayout, QHBoxLayout)
from PyQt6.QtCore import Qt, QTimer
import json

# Твой ключ API
genai.configure(api_key="ТВОЙ_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')

class QuantumTerminal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QUANTUM CORE PRO")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background: #0a0a0c; color: white; border: 1px solid #333;")
        self.setFixedSize(400, 600)
        
        self.layout = QVBoxLayout()
        
        # 1. Выбор категории и актива
        self.cat_box = QComboBox()
        self.cat_box.addItems(["Криптовалюты", "Валюты", "Акции"])
        self.layout.addWidget(self.cat_box)
        
        self.asset_box = QComboBox()
        self.asset_box.addItems(["Bitcoin OTC", "Ethereum OTC", "EUR/USD OTC"])
        self.layout.addWidget(self.asset_box)
        
        # 2. Тайминг
        self.time_box = QComboBox()
        self.time_box.addItems(["5 сек", "30 сек", "1 мин", "5 мин", "10 мин"])
        self.layout.addWidget(self.time_box)
        
        # 3. Кнопка сканирования
        self.btn = QPushButton("СКАНИРОВАТЬ ЭКРАН")
        self.btn.setStyleSheet("background: #007bff; padding: 15px; font-weight: bold;")
        self.btn.clicked.connect(self.analyze)
        self.layout.addWidget(self.btn)
        
        # 4. Вывод сигнала
        self.res_label = QLabel("Сигнал: --")
        self.res_label.setStyleSheet("font-size: 18px; margin: 10px 0;")
        self.layout.addWidget(self.res_label)
        
        # 5. Таймер и советы
        self.timer_label = QLabel("Таймер: --")
        self.layout.addWidget(self.timer_label)
        self.advice1 = QLabel("Совет 1: --")
        self.layout.addWidget(self.advice1)
        self.advice2 = QLabel("Совет 2: --")
        self.layout.addWidget(self.advice2)
        
        # 6. Кнопка перекрытия
        self.mart_btn = QPushButton("ПЕРЕКРЫТИЕ (Мартин)")
        self.mart_btn.setStyleSheet("background: #ff4757;")
        layout.addWidget(self.mart_btn)
        
        self.setLayout(self.layout)

    def analyze(self):
        # Скриншот области экрана
        img = pyautogui.screenshot() 
        img.save("graph.png")
        
        with open("graph.png", "rb") as f:
            resp = model.generate_content(["Проанализируй график, дай сигнал, 2 совета.", {"mime_type": "image/png", "data": f.read()}])
        
        self.res_label.setText(f"Сигнал: {resp.text}")
        self.start_timer(int(self.time_box.currentText().split()[0]))

    def start_timer(self, seconds):
        self.remaining = seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def update_timer(self):
        self.remaining -= 1
        self.timer_label.setText(f"Таймер: {self.remaining} сек")
        if self.remaining <= 0: self.timer.stop()

app = QApplication(sys.argv)
win = QuantumTerminal()
win.show()
sys.exit(app.exec())
