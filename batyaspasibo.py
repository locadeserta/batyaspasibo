import requests
from flask import Flask
import threading

# Токен вашего бота
TOKEN = "7861894646:AAF61HQJMsVNHGCXOwCi0GyTvEtYGTP3peY"
URL = f"https://api.telegram.org/bot{TOKEN}/"

# Имя пользователя бота, получаем из API Telegram
BOT_USERNAME = requests.get(URL + "getMe").json()["result"]["username"]

# Слова, на которые бот будет реагировать
TRIGGER_WORDS = [
    "батя", "бати", "батю", "бате", "батей", "батею",
    "бать", "батька", "батёк", "батек", "батьке", 
    "батьку", "батьки", "батьком"
]

def get_updates(offset=None):
    """Получение обновлений от Telegram."""
    params = {'offset': offset, 'timeout': 30}
    response = requests.get(URL + "getUpdates", params=params)
    return response.json()

def send_message(chat_id, text):
    """Отправка сообщения пользователю."""
    params = {'chat_id': chat_id, 'text': text}
    requests.post(URL + "sendMessage", params=params)

def check_trigger_words(text):
    """Проверяет, содержит ли текст одно из триггерных слов."""
    text_lower = text.lower()
    return any(word in text_lower for word in TRIGGER_WORDS)

def handle_message(update):
    """Обработка входящего сообщения."""
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]

        # Проверяем текст обычного сообщения
        text = message.get("text", "")

        # Проверяем пересланные сообщения
        if "forward_from_chat" in message or "forward_from" in message:
            forwarded_text = message.get("text", "")
            if check_trigger_words(forwarded_text):
                send_message(chat_id, "Спасибо!")
                return  # Отвечаем только один раз

        # Проверяем сообщения от имени группы или канала
        if "sender_chat" in message:
            sender_chat_text = message.get("text", "")
            if check_trigger_words(sender_chat_text):
                send_message(chat_id, "Спасибо!")
                return  # Отвечаем только один раз

        # Условие: упоминание бота или ключевые слова в личных/групповых сообщениях
        if (
            BOT_USERNAME in text  # Упоминание бота
            or check_trigger_words(text)  # Ключевые слова
            or message["chat"]["type"] == "private"  # Личные сообщения
        ):
            send_message(chat_id, "Спасибо!")

def main():
    """Основной цикл работы бота."""
    last_update_id = None  # Храним ID последнего обработанного сообщения

    while True:
        updates = get_updates(last_update_id)
        if "result" in updates and len(updates["result"]) > 0:
            for update in updates["result"]:
                handle_message(update)  # Обработка сообщения
                last_update_id = update["update_id"] + 1  # Сохраняем ID последнего сообщения

# Flask-сервер для работы в фоне
app = Flask('')

@app.route('/')
def home():
    return "Бот работает!"

def run():
    """Запуск Flask-сервера."""
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Запускаем сервер Flask в отдельном потоке."""
    t = threading.Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()  # Запускаем сервер Flask
    main()        # Запускаем бота
