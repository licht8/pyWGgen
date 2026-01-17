#!/usr/bin/env python3
"""AI Diagnostics Tab для Gradio."""

import gradio as gr
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import settings

from ai_assistant.data_collector import collect_all_data
from ai_assistant.ai_analyzer import analyze_with_ai
from ai_assistant.utils import save_json_log, check_ollama


def format_diagnostics_summary(data: dict) -> str:
    """Форматирование summary диагностики для Gradio."""
    
    nat = data.get("nat", {})
    fw = data.get("firewalld", {})
    wg_status = data.get("wg_status", {})
    
    # Иконки статусов
    nat_icon = "🟢" if nat.get("ok") else "🔴"
    fw_status = fw.get("active", "unknown")
    fw_icon = "🟢" if fw_status in ["running", "active"] else "🔴"
    wg_port_icon = "🟢" if fw.get("wg_port_open") else "🔴"
    ollama_icon = "🟢" if data.get("health", {}).get("ollama_ok") else "🔴"
    
    # WireGuard интерфейсы
    wg_lines = []
    for iface, info in wg_status.items():
        status_icon = "🟢" if info.get("service_active") else "🔴"
        wg_lines.append(f"  {status_icon} {iface} ({info.get('service_status')})")
    
    # Формирование вывода
    summary = f"""## 🚀 VPN ДИАГНОСТИКА

**🖥️  Сервер:** {data.get('hostname')}  
**📅 Дата:** {data.get('timestamp')}  
**⏱️  Uptime:** {data.get('uptime')}

---

### 📡 WireGuard: {data.get('wg_active')}/{data.get('wg_total')} активны

{chr(10).join(wg_lines)}

---

### 🔥 Сеть & Firewall

- **Firewalld:** {fw_icon} {fw_status}
- **WG порт:** {wg_port_icon} {fw.get('wg_port', 'N/A')}
- **NAT:** {nat_icon} {nat.get('reason', 'Нет данных')}

---

### 👥 Peers

- **Активных (подключено):** {data.get('peers_active', 0)}
- **Настроено (всего):** {data.get('peers_configured', 0)}
- **Пользовательских конфигов:** {data.get('user_peer_files', {}).get('total', 0)}

---

### 🤖 AI Assistant

- **Ollama:** {ollama_icon} {'Доступен' if data.get('health', {}).get('ollama_ok') else 'Недоступен'}
- **Host:** {settings.OLLAMA_HOST}
- **Model:** {settings.MODEL_NAME}
"""
    
    return summary


def run_diagnostics():
    """Запуск полной диагностики."""
    try:
        # Сбор данных
        data = collect_all_data()
        
        # Сохранение лога
        log_file = save_json_log(data, prefix="diag")
        
        # Форматирование summary
        summary = format_diagnostics_summary(data)
        
        # AI анализ
        if not check_ollama(settings.OLLAMA_HOST):
            ai_analysis = f"❌ **Ollama недоступен**\n\nПроверь: {settings.OLLAMA_HOST}"
        else:
            ai_analysis = analyze_with_ai(data)
        
        # Добавляем AI анализ к summary
        full_report = f"{summary}\n\n---\n\n## 🤖 АНАЛИЗ AI\n\n{ai_analysis}\n\n---\n\n**📄 Лог сохранён:** `{log_file}`"
        
        return full_report
    
    except Exception as e:
        return f"❌ **Ошибка диагностики:**\n\n```\n{str(e)}\n```"


def ai_diagnostics_tab():
    """Создание таба AI Diagnostics."""
    
    # Убрали with gr.Tab() - таб уже создан в main_interface.py
    gr.Markdown("# 🚀 AI VPN Diagnostics\n\nПолная диагностика VPN сервера с AI анализом")
    
    with gr.Row():
        run_btn = gr.Button("Запустить диагностику", scale=2)
        refresh_btn = gr.Button("Обновить", scale=1)
    
    output = gr.Markdown(
        value="Нажми **Запустить диагностику** для начала анализа",
        label="Результат диагностики"
    )
    
    # Привязка кнопок
    run_btn.click(fn=run_diagnostics, outputs=output)
    refresh_btn.click(fn=run_diagnostics, outputs=output)
