#!/usr/bin/env python3
"""Zakładka diagnostyki AI dla Gradio."""

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
    """Formatuje podsumowanie diagnostyki dla Gradio."""
    
    nat = data.get("nat", {})
    fw = data.get("firewalld", {})
    wg_status = data.get("wg_status", {})
    
    # Ikony statusów
    nat_icon = "🟢" if nat.get("ok") else "🔴"
    fw_status = fw.get("active", "nieznany")
    fw_icon = "🟢" if fw_status in ["running", "active"] else "🔴"
    wg_port_icon = "🟢" if fw.get("wg_port_open") else "🔴"
    ollama_icon = "🟢" if data.get("health", {}).get("ollama_ok") else "🔴"
    
    # Interfejsy WireGuard
    wg_lines = []
    for iface, info in wg_status.items():
        status_icon = "🟢" if info.get("service_active") else "🔴"
        wg_lines.append(f"  {status_icon} {iface} ({info.get('service_status')})")
    
    # Formatowanie wyniku
    summary = f"""## 🚀 Diagnostyka VPN

**🖥️  Serwer:** {data.get('hostname')}  
**📅 Data:** {data.get('timestamp')}  
**⏱️  Uptime:** {data.get('uptime')}

---

### 📡 WireGuard: {data.get('wg_active')}/{data.get('wg_total')} aktywnych

{chr(10).join(wg_lines)}

---

### 🔥 Sieć & Firewall

- **Firewalld:** {fw_icon} {fw_status}
- **Port WG:** {wg_port_icon} {fw.get('wg_port', 'N/A')}
- **NAT:** {nat_icon} {nat.get('reason', 'Brak danych')}

---

### 👥 Peers

- **Aktywnych (połączonych):** {data.get('peers_active', 0)}
- **Skonfigurowanych (łącznie):** {data.get('peers_configured', 0)}
- **Plików konfiguracyjnych użytkowników:** {data.get('user_peer_files', {}).get('total', 0)}

---

### 🤖 Asystent AI

- **Ollama:** {ollama_icon} {'Dostępny' if data.get('health', {}).get('ollama_ok') else 'Niedostępny'}
- **Host:** {settings.OLLAMA_HOST}
- **Model:** {settings.MODEL_NAME}
"""
    
    return summary


def run_diagnostics():
    """Uruchamia pełną diagnostykę."""
    try:
        # Zbierz dane
        data = collect_all_data()
        
        # Zapisz log
        log_file = save_json_log(data, prefix="diag")
        
        # Sformatuj podsumowanie
        summary = format_diagnostics_summary(data)
        
        # Analiza AI
        if not check_ollama(settings.OLLAMA_HOST):
            ai_analysis = f"❌ **Ollama niedostępny**\n\nSprawdź: {settings.OLLAMA_HOST}"
        else:
            ai_analysis = analyze_with_ai(data)
        
        # Połącz podsumowanie z analizą AI
        full_report = f"{summary}\n\n---\n\n## 🤖 ANALIZA AI\n\n{ai_analysis}\n\n---\n\n**📄 Log zapisany:** `{log_file}`"
        
        return full_report
    
    except Exception as e:
        return f"❌ **Błąd diagnostyki:**\n\n```\n{str(e)}\n```"


def ai_diagnostics_tab():
    """Tworzy zakładkę Diagnostyki AI."""
    
    # Bez with gr.Tab() - zakładka utworzona w main_interface.py
    gr.Markdown("# 🚀 Diagnostyka VPN AI\n\nPełna diagnostyka serwera VPN z analizą AI")
    
    with gr.Row():
        run_btn = gr.Button("Uruchom diagnostykę", scale=2)
        refresh_btn = gr.Button("Odśwież", scale=1)
    
    output = gr.Markdown(
        value="Naciśnij **Uruchom diagnostykę** aby rozpocząć analizę",
        label="Wynik diagnostyki"
    )
    
    # Powiązanie przycisków
    run_btn.click(fn=run_diagnostics, outputs=output)
    refresh_btn.click(fn=run_diagnostics, outputs=output)
