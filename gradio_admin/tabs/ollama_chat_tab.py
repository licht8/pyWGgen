import gradio as gr
import requests
import json
import logging
import sys
from datetime import datetime

# Настройка логирования с принудительным выводом в консоль
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Создаем форматтер для логов
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Хендлер для консоли
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Хендлер для файла
file_handler = logging.FileHandler(f'ollama_chat_{datetime.now().strftime("%Y%m%d")}.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Добавляем хендлеры к логгеру
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Отключаем распространение логов выше
logger.propagate = False

def chat_with_ollama(message, history, model="llama2"):
    """Функция для общения с Ollama API"""
    # Логируем входящий запрос
    logger.info("\n" + "=" * 50)
    logger.info(f"Новый запрос к модели {model}")
    logger.info(f"Пользователь: {message}")
    logger.info("-" * 50)
    
    if not message:
        logger.warning("Получено пустое сообщение")
        return "", history
    
    api_url = "http://10.67.67.2:11434/api/generate"
    
    try:
        # Отправка запроса
        logger.info(f"Отправка запроса к {api_url}")
        response = requests.post(api_url, json={
            "model": model,
            "prompt": message,
            "stream": False
        })
        response.raise_for_status()
        
        result = response.json()
        assistant_response = result.get("response", "Ошибка: нет ответа")
        
        # Логируем ответ ассистента
        logger.info(f"Ассистент: {assistant_response}")
        logger.info("=" * 50)
        
        new_message = {
            "role": "assistant",
            "content": assistant_response
        }
        
        return "", history + [
            {"role": "user", "content": message},
            new_message
        ]
    
    except Exception as e:
        error_msg = f"Ошибка: {str(e)}"
        logger.error(f"Произошла ошибка: {error_msg}")
        logger.info("=" * 50)
        return error_msg, history

def list_models():
    """Получение списка доступных моделей"""
    logger.info("Запрос списка моделей...")
    try:
        response = requests.get("http://10.67.67.2:11434/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json()
        logger.info(f"Получен список моделей: {json.dumps(models, ensure_ascii=False)}")
        return [model["name"] for model in models["models"]]
    except Exception as e:
        logger.error(f"Ошибка при получении списка моделей: {str(e)}")
        return ["llama2"]

def ollama_chat_tab():
    """Создание интерфейса вкладки чата"""
    logger.info("Инициализация интерфейса чата")
    
    with gr.Column():
        # Информационное сообщение о статусе
        status = gr.Textbox(
            label="Статус подключения",
            interactive=False
        )
        
        # Выпадающий список для выбора модели
        available_models = list_models()
        logger.info(f"Доступные модели: {available_models}")
        
        model_dropdown = gr.Dropdown(
            choices=available_models,
            value=available_models[0] if available_models else "llama2",
            label="Выберите модель"
        )
        
        # Компонент чата
        chatbot = gr.Chatbot(
            label="Диалог с Ollama",
            type="messages"
        )
        
        # Поле ввода сообщения
        msg = gr.Textbox(
            label="Введите сообщение",
            placeholder="Напишите что-нибудь... (Shift+Enter для отправки)",
            lines=3
        )
        
        # Кнопки
        with gr.Row():
            submit = gr.Button("Отправить")
            clear = gr.Button("Очистить историю")
        
        # Обработчики событий
        def update_status():
            try:
                logger.info("Проверка подключения к Ollama API...")
                response = requests.get("http://10.67.67.2:11434/api/version", timeout=5)
                logger.info(f"Получен ответ: {response.text}")
                version = response.json().get("version", "неизвестно")
                status_msg = f"✅ Подключено к Ollama API (версия {version})"
                logger.info(status_msg)
                return status_msg
            except Exception as e:
                error_msg = f"❌ Нет подключения к Ollama API: {str(e)}"
                logger.error(error_msg)
                return error_msg
        
        # Обновление статуса при загрузке
        status.value = update_status()
        
        submit.click(
            chat_with_ollama,
            inputs=[msg, chatbot, model_dropdown],
            outputs=[msg, chatbot]
        )
        
        msg.submit(
            chat_with_ollama,
            inputs=[msg, chatbot, model_dropdown],
            outputs=[msg, chatbot]
        )
        
        clear.click(lambda: [], None, chatbot, queue=False)

    logger.info("Интерфейс чата инициализирован")
