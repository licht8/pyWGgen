import gradio as gr
import requests
import json
import logging
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ollama_chat.log')
    ]
)
logger = logging.getLogger(__name__)

def chat_with_ollama(message, history, model="llama2"):
    """Функция для общения с Ollama API"""
    logger.debug(f"Получено сообщение: {message}")
    logger.debug(f"Текущая история: {history}")
    logger.debug(f"Выбранная модель: {model}")
    
    if not message:
        logger.warning("Получено пустое сообщение")
        return "", history
    
    api_url = "http://10.67.67.2:11434/api/generate"
    logger.debug(f"API URL: {api_url}")
    
    # Собираем контекст из истории
    context = "\n".join([f"Human: {h[0]}\nAssistant: {h[1]}" for h in history])
    
    payload = {
        "model": model,
        "prompt": message,
        "context": context,
        "stream": False
    }
    logger.debug(f"Отправляемый payload: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        logger.debug("Отправка запроса к API...")
        response = requests.post(api_url, json=payload, timeout=30)
        logger.debug(f"Получен ответ со статусом: {response.status_code}")
        response.raise_for_status()
        
        result = response.json()
        logger.debug(f"Получен JSON ответ: {json.dumps(result, ensure_ascii=False)}")
        
        return result.get("response", "Ошибка: нет ответа"), history + [[message, result.get("response", "")]]
    
    except requests.exceptions.Timeout:
        error_msg = "Превышено время ожидания ответа от API"
        logger.error(error_msg)
        return error_msg, history
    except requests.exceptions.RequestException as e:
        error_msg = f"Ошибка при обращении к API: {str(e)}"
        logger.error(error_msg)
        return error_msg, history
    except json.JSONDecodeError as e:
        error_msg = f"Ошибка декодирования JSON: {str(e)}"
        logger.error(error_msg)
        return error_msg, history
    except Exception as e:
        error_msg = f"Неожиданная ошибка: {str(e)}"
        logger.error(error_msg)
        return error_msg, history

def list_models():
    """Получение списка доступных моделей"""
    logger.debug("Запрос списка моделей...")
    try:
        response = requests.get("http://10.67.67.2:11434/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json()
        logger.debug(f"Получен список моделей: {json.dumps(models, ensure_ascii=False)}")
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
        logger.debug(f"Доступные модели: {available_models}")
        
        model_dropdown = gr.Dropdown(
            choices=available_models,
            value=available_models[0] if available_models else "llama2",
            label="Выберите модель"
        )
        
        # Компонент чата
        chatbot = gr.Chatbot(
            height=400,
            show_copy_button=True,
            label="Диалог с Ollama"
        )
        
        # Поле ввода сообщения
        msg = gr.Textbox(
            label="Введите сообщение",
            placeholder="Напишите что-нибудь...",
            lines=3
        )
        
        # Кнопки
        with gr.Row():
            submit = gr.Button("Отправить")
            clear = gr.Button("Очистить историю")
        
        # Обработчики событий
        def update_status():
            try:
                response = requests.get("http://10.67.67.2:11434/api/version", timeout=5)
                version = response.json().get("version", "неизвестно")
                return f"✅ Подключено к Ollama API (версия {version})"
            except:
                return "❌ Нет подключения к Ollama API"
        
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
        
        clear.click(lambda: None, None, chatbot, queue=False)

    logger.info("Интерфейс чата инициализирован")

# Необходимые зависимости (добавьте в requirements.txt):
# gradio>=3.50.2
# requests>=2.31.0
# python-json-logger>=2.0.7
