import pyautogui
import cv2
import numpy as np

class ScreenScanner:
    def __init__(self, region=None):
        # region задает область экрана (x, y, width, height)
        self.region = region

    def capture(self):
        # Делаем скриншот
        screenshot = pyautogui.screenshot(region=self.region)
        # Превращаем в формат, понятный OpenCV (массив)
        frame = np.array(screenshot)
        # Конвертируем цвета (OpenCV использует BGR, а не RGB)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame

    def save_debug_image(self, frame, filename="debug_scan.png"):
        cv2.imwrite(filename, frame)
        print(f"Скриншот сохранен как {filename}")

# Пример использования (можно проверить работу модуля отдельно)
if __name__ == "__main__":
    # Укажите координаты вашей области (например: 100, 100, 800, 600)
    # Или оставьте None для всего экрана
    scanner = ScreenScanner(region=(100, 100, 800, 600))
    img = scanner.capture()
    scanner.save_debug_image(img)
