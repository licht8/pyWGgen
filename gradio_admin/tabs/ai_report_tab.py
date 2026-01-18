#!/usr/bin/env python3
"""Zakładka generatora raportów AI dla Gradio."""

import gradio as gr
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import settings

from ai_assistant.data_collector import collect_all_data
from ai_assistant.ai_report import generate_report, get_report_dir


def generate_html_report():
    """Generuje raport HTML."""
    try:
        # Zbierz dane
        data = collect_all_data()
        
        # Wygeneruj raport
        report_path = generate_report(data)
        
        # Sprawdź rozmiar pliku
        file_size_kb = os.path.getsize(report_path) / 1024
        
        info = f"""✅ **Raport pomyślnie wygenerowany!**

**📄 Plik:** `{report_path}`

**📊 Rozmiar:** {file_size_kb:.1f} KB

**💡 Użyj przycisku "Pobierz" poniżej**
"""
        
        return info, report_path
    
    except Exception as e:
        error_info = f"❌ **Błąd:** {str(e)}"
        return error_info, None


def list_previous_reports():
    """Lista poprzednich raportów."""
    try:
        report_dir = get_report_dir()
        reports = sorted(report_dir.glob("report_*.html"), reverse=True)
        
        if not reports:
            return "📭 **Brak zapisanych raportów**", None
        
        report_list = "## 📋 Poprzednie raporty\n\n"
        for i, report in enumerate(reports[:10], 1):
            size_kb = report.stat().st_size / 1024
            report_list += f"{i}. `{report.name}` — {size_kb:.1f} KB\n"
        
        report_list += f"\n**Łącznie raportów:** {len(reports)}"
        
        return report_list, None
    
    except Exception as e:
        return f"❌ **Błąd:** {str(e)}", None


def ai_report_tab():
    """Tworzy zakładkę generatora raportów AI."""
    
    gr.Markdown("# 📄 Generator raportów AI\n\nGenerowanie szczegółowych raportów HTML o stanie serwera VPN")
    
    with gr.Row():
        generate_btn = gr.Button("Wygeneruj raport", size="lg")
        list_btn = gr.Button("Lista raportów", size="lg")
    
    info_output = gr.Markdown(value="Naciśnij **Wygeneruj raport** aby utworzyć nowy raport")
    
    download_file = gr.File(label="💾 Pobierz raport HTML")
    
    generate_btn.click(
        fn=generate_html_report,
        outputs=[info_output, download_file]
    )
    
    list_btn.click(
        fn=list_previous_reports,
        outputs=[info_output, download_file]
    )
