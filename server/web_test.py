# client.py
import requests
import time
import json

# УКАЖИ СЮДА АДРЕС СЕРВЕРА
# Для теста на одном ПК:
SERVER_URL = "http://127.0.0.1:5000"


# Когда перенесёшь на Raspberry Pi — замени на её IP, например:
# SERVER_URL = "http://192.168.1.35:5000"

def send_command(command):
    url = f"{SERVER_URL}/send"
    data = {"command": command, "from": "main_pc", "timestamp": time.time()}
    try:
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            print(f"Команда отправлена: {command}")
        else:
            print(f"Ошибка отправки: {response.status_code}")
    except Exception as e:
        print(f"Не удалось соединиться с сервером: {e}")


def get_data_from_rpi():
    try:
        response = requests.get(f"{SERVER_URL}/get", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("Данные с Raspberry Pi:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
        else:
            print("Сервер вернул ошибку")
    except Exception as e:
        print(f"Нет связи с Raspberry Pi: {e}")
    return None


# === ТЕСТОВЫЙ ЦИКЛ ===
if __name__ == "__main__":
    print("Клиент запущен. Отправка тестовых команд каждые 3 секунды...")
    print(f"Подключение к: {SERVER_URL}")
    print("Нажми Ctrl+C для выхода\n")

    commands = ["включи свет", "выключи свет", "статус", "перезагрузка", "привет от ПК"]
    i = 0

    try:
        while True:
            cmd = commands[i % len(commands)]
            send_command(cmd)
            time.sleep(1)

            get_data_from_rpi()
            print("-" * 50)

            i += 1
            time.sleep(3)
    except KeyboardInterrupt:
        print("\nКлиент остановлен.")