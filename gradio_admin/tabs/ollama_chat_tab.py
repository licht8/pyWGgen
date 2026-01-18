#!/usr/bin/env python3
"""Zakładka chatu AI dla Gradio."""

import gradio as gr
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import settings

from ai_assistant.data_collector import collect_all_data
from ai_assistant.ai_chat import ask_question
from ai_assistant.utils import check_ollama, run_cmd

# Globalne ustawienia AI
ai_settings = {
    "temperature": 0.7,
    "max_tokens": 2000,
    "system_prompt": "Jesteś doświadczonym administratorem systemowym, specjalizującym się w WireGuard VPN. Odpowiadaj po polsku, bądź precyzyjny i konkretny."
}


def load_ai_help() -> str:
    """Wczytuje pomoc AI z pliku."""
    help_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "ai_assistant",
        "ai_help.md"
    )
    
    try:
        with open(help_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"❌ Błąd wczytywania pomocy: {str(e)}"


def get_server_context_html() -> str:
    """Pobiera kontekst serwera w formacie HTML."""
    try:
        data = collect_all_data()
        
        nat = data.get("nat", {})
        fw = data.get("firewalld", {})
        wg_status = data.get("wg_status", {})
        
        # Zewnętrzny IP
        external_ip = run_cmd("curl -s ifconfig.me") or "N/A"
        
        # Wewnętrzny IP WireGuard
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
        ollama_status = "🟢 Dostępny" if data.get("health", {}).get("ollama_ok") else "🔴 Niedostępny"
        nat_status = "🟢 OK" if nat.get("ok") else "🔴 Problem"
        
        context = f"""**🖥️  Hostname:** {data.get('hostname')}  
**🌐 Zewnętrzny IP:** {external_ip}  
**🔧 Uptime:** {data.get('uptime')}

---

**📡 Interfejs WireGuard:** {wg_interface}  
**🔗 IP tunelu:** {wg_internal_ip}  
**🔌 Port:** {wg_port}  
**📊 Status:** {data.get('wg_active')}/{data.get('wg_total')} aktywnych

---

**👥 Peers:**
- Aktywnych: {data.get('peers_active', 0)}
- Skonfigurowanych: {data.get('peers_configured', 0)}
- Użytkowników: {data.get('user_peer_files', {}).get('total', 0)}

---

**🔥 Firewalld:** {fw.get('active')}  
**🛡️  NAT:** {nat_status}  
**🤖 Ollama:** {ollama_status}  
**🧠 Model:** {settings.MODEL_NAME}
"""
        
        return context
    
    except Exception as e:
        return f"❌ **Błąd wczytywania kontekstu:**\n\n```\n{str(e)}\n```"


def update_ai_settings(temperature, max_tokens, system_prompt):
    """Aktualizuje ustawienia AI."""
    ai_settings["temperature"] = temperature
    ai_settings["max_tokens"] = max_tokens
    ai_settings["system_prompt"] = system_prompt
    return f"✅ Ustawienia AI zaktualizowane:\n- Temperatura: {temperature}\n- Max tokenów: {max_tokens}"


def chat_with_ai(message, history):
    """Chat z AI (dla Gradio ChatInterface)."""
    try:
        # Zbierz dane
        data = collect_all_data()
        
        # Sprawdź Ollama
        if not check_ollama(settings.OLLAMA_HOST):
            return f"❌ Ollama niedostępny. Sprawdź: {settings.OLLAMA_HOST}"
        
        # Otrzymaj odpowiedź od AI
        response = ask_question(data, message)
        
        return response
    
    except Exception as e:
        return f"❌ Błąd: {str(e)}"


def ollama_chat_tab():
    """Tworzy zakładkę chatu AI."""
    
    gr.Markdown("# 💬 Chat AI - Tryb interaktywny\n\nZadawaj pytania dotyczące serwera VPN")
    
    with gr.Row():
        # Chat po lewej (70% szerokości)
        with gr.Column(scale=7):
            gr.ChatInterface(
                fn=chat_with_ai,
                chatbot=gr.Chatbot(height=500),
                textbox=gr.Textbox(placeholder="Napisz pytanie...", container=False, scale=7),
                examples=[
                    "Ile peers jest podłączonych?",
                    "Jaki jest mój zewnętrzny IP?",
                    "Pokaż status WireGuard",
                    "Jak dodać nowego użytkownika?",
                    "Sprawdź działanie NAT"
                ]
            )
        
        # Ustawienia po prawej (30% szerokości)
        with gr.Column(scale=3):
            
            # Kontekst serwera
            with gr.Accordion("Kontekst serwera", open=False, elem_id="server_context_accordion"):
                context_output = gr.Markdown(value=get_server_context_html())
                refresh_context_btn = gr.Button("Odśwież", variant="secondary", size="sm")
                refresh_context_btn.click(fn=get_server_context_html, outputs=context_output)
            
            # Ustawienia AI
            with gr.Accordion("Ustawienia AI", open=False, elem_id="ai_settings_accordion"):
                
                temperature_slider = gr.Slider(
                    minimum=0.0,
                    maximum=2.0,
                    value=ai_settings["temperature"],
                    step=0.1,
                    label="Temperatura",
                    info="Kreatywność"
                )
                
                max_tokens_slider = gr.Slider(
                    minimum=500,
                    maximum=4000,
                    value=ai_settings["max_tokens"],
                    step=100,
                    label="Max tokenów",
                    info="Długość odpowiedzi"
                )
                
                system_prompt_text = gr.Textbox(
                    value=ai_settings["system_prompt"],
                    label="System Prompt",
                    lines=3,
                    info="Zachowanie AI"
                )
                
                with gr.Row():
                    save_settings_btn = gr.Button("Zapisz", variant="primary", size="sm")
                    reset_settings_btn = gr.Button("Resetuj", variant="secondary", size="sm")
                
                settings_status = gr.Markdown(value="")
                
                # Obsługa przycisków
                save_settings_btn.click(
                    fn=update_ai_settings,
                    inputs=[temperature_slider, max_tokens_slider, system_prompt_text],
                    outputs=settings_status
                )
                
                def reset_settings():
                    return (
                        0.7,
                        2000,
                        "Jesteś doświadczonym administratorem systemowym, specjalizującym się w WireGuard VPN. Odpowiadaj po polsku, bądź precyzyjny i konkretny.",
                        "🔄 Ustawienia zresetowane"
                    )
                
                reset_settings_btn.click(
                    fn=reset_settings,
                    outputs=[temperature_slider, max_tokens_slider, system_prompt_text, settings_status]
                )
            
            # Pomoc do ustawień AI
            with gr.Accordion("Pomoc do ustawień", open=False, elem_id="ai_help_accordion"):
                gr.Markdown(value=load_ai_help())
