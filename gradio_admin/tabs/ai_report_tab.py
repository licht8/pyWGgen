#!/usr/bin/env python3
"""AI Report Tab для Gradio."""

import gradio as gr
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import settings

from ai_assistant.data_collector import collect_all_data
from ai_assistant.ai_report import generate_report, get_report_dir


def generate_html_report():
    """Генерация HTML отчёта."""
    try:
        # Сбор данных
        data = collect_all_data()
        
        # Генерация отчёта
        report_path = generate_report(data)
        
        # Читаем размер файла
        file_size_kb = os.path.getsize(report_path) / 1024
        
        info = f"""✅ **Отчёт успешно сгенерирован!**

**📄 Файл:** `{report_path}`

**📊 Размер:** {file_size_kb:.1f} KB

**💡 Используй кнопку "Скачать" ниже**
"""
        
        return info, report_path
    
    except Exception as e:
        error_info = f"❌ **Ошибка:** {str(e)}"
        return error_info, None


def list_previous_reports():
    """Список предыдущих отчётов."""
    try:
        report_dir = get_report_dir()
        reports = sorted(report_dir.glob("report_*.html"), reverse=True)
        
        if not reports:
            return "📭 **Нет сохранённых отчётов**", None
        
        report_list = "## 📋 Предыдущие отчёты\n\n"
        for i, report in enumerate(reports[:10], 1):
            size_kb = report.stat().st_size / 1024
            report_list += f"{i}. `{report.name}` — {size_kb:.1f} KB\n"
        
        report_list += f"\n**Всего отчётов:** {len(reports)}"
        
        return report_list, None
    
    except Exception as e:
        return f"❌ **Ошибка:** {str(e)}", None


def ai_report_tab():
    """Создание таба AI Report."""
    
    gr.Markdown("# 📄 AI Report Generator\n\nГенерация подробных HTML отчётов о состоянии VPN сервера")
    
    with gr.Row():
        generate_btn = gr.Button("Сгенерировать отчёт", size="lg")
        list_btn = gr.Button("Список отчётов", size="lg")
    
    info_output = gr.Markdown(value="Нажми **Сгенерировать отчёт** для создания нового отчёта")
    
    download_file = gr.File(label="💾 Скачать HTML отчёт")
    
    generate_btn.click(
        fn=generate_html_report,
        outputs=[info_output, download_file]
    )
    
    list_btn.click(
        fn=list_previous_reports,
        outputs=[info_output, download_file]
    )
