# simple_client_fixed.py
import cv2
import time  # ← добавили импорт!

# Замени на реальный IP твоей Raspberry Pi
url = 'http://192.168.1.23:5000/'

cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("Ошибка подключения! Проверь IP, порт и что сервер запущен.")
    exit()

print("Подключено! Нажми 'q' — выход, 's' — сохранить текущий кадр")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Кадр не получен, переподключаемся...")
        cap.release()
        cap = cv2.VideoCapture(url)
        time.sleep(1)  # небольшая пауза перед повторным подключением
        continue

    cv2.imshow('Raspberry Pi Camera', frame)

    # Один-единственный waitKey — это важно!
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        print("Выход...")
        break
    elif key == ord('s'):
        filename = f"capture_{int(time.time())}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Сохранено → {filename}")

# Правильная очистка
cap.release()
cv2.destroyAllWindows()