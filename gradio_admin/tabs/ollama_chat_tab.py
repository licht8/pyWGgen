#!/usr/bin/env python3
"""AI Chat Tab для Gradio."""

import gradio as gr
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import settings

from ai_assistant.data_collector import collect_all_data
from ai_assistant.ai_chat import ask_question
from ai_assistant.utils import check_ollama, run_cmd

# Глобальные настройки AI
ai_settings = {
    "temperature": 0.7,
    "max_tokens": 2000,
    "system_prompt": "Ты опытный системный администратор, специализирующийся на WireGuard VPN. Отвечай на русском языке, будь точным и конкретным."
}


def load_ai_help() -> str:
    """Загрузить справку по AI из файла."""
    help_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "ai_assistant",
        "ai_help.md"
    )
    
    try:
        with open(help_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"❌ Ошибка загрузки справки: {str(e)}"


def get_server_context_html() -> str:
    """Получить HTML контекст сервера."""
    try:
        data = collect_all_data()
        
        nat = data.get("nat", {})
        fw = data.get("firewalld", {})
        wg_status = data.get("wg_status", {})
        
        # Внешний IP
        external_ip = run_cmd("curl -s ifconfig.me") or "N/A"
        
        # Внутренний IP WireGuard
        wg_internal_ip = "N/A"
        wg_interface = "N/A"
        for iface, info in wg_status.items():
            if iface == "wg-mgmt":
                continue
            if info.get("service_active"):
                wg_interface = iface
                ip_output = run_cmd(f"ip addr show {iface} | grep 'inet ' | awk '{{print $2}}'")
                if ip_output:
                    wg_internal_ip = ip_output.split('\n')[0]
                break
        
        wg_port = fw.get('wg_port', 'N/A')
        ollama_status = "🟢 Доступен" if data.get("health", {}).get("ollama_ok") else "🔴 Недоступен"
        nat_status = "🟢 OK" if nat.get("ok") else "🔴 Проблема"
        
        context = f"""**🖥️  Hostname:** {data.get('hostname')}  
**🌐 External IP:** {external_ip}  
**🔧 Uptime:** {data.get('uptime')}

---

**📡 WireGuard Interface:** {wg_interface}  
**🔗 Tunnel IP:** {wg_internal_ip}  
**🔌 Port:** {wg_port}  
**📊 Status:** {data.get('wg_active')}/{data.get('wg_total')} активны

---

**👥 Peers:**
- Активных: {data.get('peers_active', 0)}
- Настроено: {data.get('peers_configured', 0)}
- Пользовательских: {data.get('user_peer_files', {}).get('total', 0)}

---

**🔥 Firewalld:** {fw.get('active')}  
**🛡️  NAT:** {nat_status}  
**🤖 Ollama:** {ollama_status}  
**🧠 Model:** {settings.MODEL_NAME}
"""
        
        return context
    
    except Exception as e:
        return f"❌ **Ошибка загрузки контекста:**\n\n```\n{str(e)}\n```"


def update_ai_settings(temperature, max_tokens, system_prompt):
    """Обновить настройки AI."""
    ai_settings["temperature"] = temperature
    ai_settings["max_tokens"] = max_tokens
    ai_settings["system_prompt"] = system_prompt
    return f"✅ Настройки AI обновлены:\n- Temperature: {temperature}\n- Max tokens: {max_tokens}"


def chat_with_ai(message, history):
    """Чат с AI (для Gradio ChatInterface)."""
    try:
        # Собираем данные
        data = collect_all_data()
        
        # Проверка Ollama
        if not check_ollama(settings.OLLAMA_HOST):
            return f"❌ Ollama недоступен. Проверь: {settings.OLLAMA_HOST}"
        
        # Получаем ответ от AI (пока используем стандартные настройки)
        # TODO: передать ai_settings в ask_question если поддерживается
        response = ask_question(data, message)
        
        return response
    
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"


def ollama_chat_tab():
    """Создание таба AI Chat."""
    
    gr.Markdown("# 💬 AI Chat - Интерактивный режим\n\nЗадавай вопросы по VPN серверу")
    
    with gr.Row():
        # Чат слева (70% ширины)
        with gr.Column(scale=7):
            gr.ChatInterface(
                fn=chat_with_ai,
                chatbot=gr.Chatbot(height=500),
                textbox=gr.Textbox(placeholder="Напиши вопрос...", container=False, scale=7),
                examples=[
                    "Сколько peers подключено?",
                    "Какой у меня внешний IP?",
                    "Покажи статус WireGuard",
                    "Как добавить нового пользователя?",
                    "Проверь работу NAT"
                ]
            )
        
        # Настройки справа (30% ширины)
        with gr.Column(scale=3):
            
            # Контекст сервера
            with gr.Accordion("Контекст сервера", open=False, elem_id="server_context_accordion"):
                context_output = gr.Markdown(value=get_server_context_html())
                refresh_context_btn = gr.Button("Обновить", variant="secondary", size="sm")
                refresh_context_btn.click(fn=get_server_context_html, outputs=context_output)
            
            # Настройки AI
            with gr.Accordion("Настройки AI", open=False, elem_id="ai_settings_accordion"):
                
                temperature_slider = gr.Slider(
                    minimum=0.0,
                    maximum=2.0,
                    value=ai_settings["temperature"],
                    step=0.1,
                    label="Temperature",
                    info="Креативность"
                )
                
                max_tokens_slider = gr.Slider(
                    minimum=500,
                    maximum=4000,
                    value=ai_settings["max_tokens"],
                    step=100,
                    label="Max Tokens",
                    info="Длина ответа"
                )
                
                system_prompt_text = gr.Textbox(
                    value=ai_settings["system_prompt"],
                    label="System Prompt",
                    lines=3,
                    info="Поведение AI"
                )
                
                with gr.Row():
                    save_settings_btn = gr.Button("Сохранить", variant="primary", size="sm")
                    reset_settings_btn = gr.Button("Сбросить", variant="secondary", size="sm")
                
                settings_status = gr.Markdown(value="")
                
                # Обработчики
                save_settings_btn.click(
                    fn=update_ai_settings,
                    inputs=[temperature_slider, max_tokens_slider, system_prompt_text],
                    outputs=settings_status
                )
                
                def reset_settings():
                    return (
                        0.7,
                        2000,
                        "Ты опытный системный администратор, специализирующийся на WireGuard VPN. Отвечай на русском языке, будь точным и конкретным.",
                        "🔄 Настройки сброшены"
                    )
                
                reset_settings_btn.click(
                    fn=reset_settings,
                    outputs=[temperature_slider, max_tokens_slider, system_prompt_text, settings_status]
                )
            
            # Справка по настройкам AI (загружается из файла)
            with gr.Accordion("Справка по настройкам", open=False, elem_id="ai_help_accordion"):
                gr.Markdown(value=load_ai_help())
