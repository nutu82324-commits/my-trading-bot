import tkinter as tk
from tkinter import ttk

class AIMasterScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Master Scanner")
        self.root.geometry("800x500")
        self.root.configure(bg="#2c3e50")

        # 1. Заголовок
        label = tk.Label(root, text="AI MASTER SCANNER", fg="white", bg="#2c3e50", font=("Arial", 16, "bold"))
        label.pack(pady=10)

        # 2. Выбор стратегии
        tk.Label(root, text="Выберите стратегию:", fg="white", bg="#2c3e50").pack()
        self.strategy_var = ttk.Combobox(root, values=["SMART MONEY", "SMT DIVERGENCE", "BREAKER BLOCK", "ICT SILVER BULLET"])
        self.strategy_var.pack(pady=5)

        # 3. Таймфрейм и экспирация (пример кнопок)
        frame_controls = tk.Frame(root, bg="#2c3e50")
        frame_controls.pack(pady=20)
        
        tk.Button(frame_controls, text="M1", command=lambda: print("Таймфрейм M1")).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_controls, text="M5", command=lambda: print("Таймфрейм M5")).pack(side=tk.LEFT, padx=5)

        # 4. Кнопка активации
        self.btn_activate = tk.Button(root, text="ACTIVATE AI SCANNER", command=self.activate_scanner, bg="#e74c3c", fg="white", font=("Arial", 12, "bold"))
        self.btn_activate.pack(pady=20)

    def activate_scanner(self):
        print("Сканер активирован! Запуск захвата экрана...")
        # Здесь будет вызов функции из scanner.py

if __name__ == "__main__":
    root = tk.Tk()
    app = AIMasterScannerApp(root)
    root.mainloop()
