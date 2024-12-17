import gradio as gr
import requests
import json

def chat_with_ollama(message, history, model="llama2"):
    """Функция для общения с Ollama API"""
    if not message:
        return "", history
    
    # Формируем запрос к API
    api_url = "http://10.67.67.2:11434/api/generate"
    
    # Собираем контекст из истории
    context = "\n".join([f"Human: {h[0]}\nAssistant: {h[1]}" for h in history])
    
    payload = {
        "model": model,
        "prompt": message,
        "context": context,
        "stream": False
    }
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "Ошибка: нет ответа"), history + [[message, result.get("response", "")]]
    except requests.exceptions.RequestException as e:
        return f"Ошибка при обращении к API: {str(e)}", history

def list_models():
    """Получение списка доступных моделей"""
    try:
        response = requests.get("http://10.67.67.2:11434/api/tags")
        response.raise_for_status()
        models = response.json()
        return [model["name"] for model in models["models"]]
    except:
        return ["llama2"]  # Возвращаем базовую модель в случае ошибки

def ollama_chat_tab():
    """Создание интерфейса вкладки чата"""
    with gr.Column():
        # Выпадающий список для выбора модели
        model_dropdown = gr.Dropdown(
            choices=list_models(),
            value="llama2",
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
        
        # Кнопка отправки
        submit = gr.Button("Отправить")
        
        # Кнопка очистки
        clear = gr.Button("Очистить историю")
        
        # Обработчики событий
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
