#!/usr/bin/env python3
# modules/gradio_utils.py

import os
import subprocess
from gradio_admin.main_interface import admin_interface
from modules.firewall_utils import open_firewalld_port, close_firewalld_port, handle_port_conflict, get_external_ip

custom_css = """
/* Wyśrodkowanie kontenera */
.gradio-container {
    max-width: 75% !important;
    width: 75% !important;
    margin: 0 auto !important;
}

/* Kompaktowe przyciski */
button {
    max-width: 220px !important;
}

/* Usuwanie obramowania tabeli HTML */
#statistics_table table {
    border: none !important;
}

#statistics_table div {
    border: none !important;
}

/* Eleganckie Accordiony BEZ ramki - tylko nagłówek */
#server_context_accordion,
#ai_settings_accordion,
#ai_help_accordion,
#report_preview_accordion {
    border: none !important;
    border-radius: 0 !important;
    background-color: transparent !important;
    overflow: visible !important;
    margin-bottom: 6px !important;
}

/* Nagłówek Accordiona - szary blok */
#server_context_accordion .label-wrap,
#ai_settings_accordion .label-wrap,
#ai_help_accordion .label-wrap,
#report_preview_accordion .label-wrap {
    background-color: #27272a !important;
    padding: 12px 16px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    color: #e5e7eb !important;
    cursor: pointer !important;
    transition: background-color 0.2s ease !important;
    display: flex !important;
    flex-direction: row-reverse !important;
    justify-content: space-between !important;
    align-items: center !important;
    border-radius: 8px !important;
}

#server_context_accordion .label-wrap:hover,
#ai_settings_accordion .label-wrap:hover,
#ai_help_accordion .label-wrap:hover,
#report_preview_accordion .label-wrap:hover {
    background-color: #2d2d30 !important;
}

#server_context_accordion .icon,
#ai_settings_accordion .icon,
#ai_help_accordion .icon,
#report_preview_accordion .icon {
    color: #9ca3af !important;
    width: 18px !important;
    height: 18px !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    flex-shrink: 0 !important;
}

/* Zawartość Accordiona - bez ramki */
#server_context_accordion > div:last-child,
#ai_settings_accordion > div:last-child,
#ai_help_accordion > div:last-child,
#report_preview_accordion > div:last-child {
    background-color: transparent !important;
    padding: 10px 0 !important;
    border: none !important;
}

/* Kontener HTML Raportu AI - KLUCZOWE STYLE */
#report_html_container {
    min-height: 600px !important;
    max-height: 800px !important;
    overflow-y: auto !important;
    background-color: #ffffff !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 8px !important;
    padding: 0 !important;
    margin-top: 10px !important;
}

/* Poprawka dla iframe wewnątrz komponentu HTML */
#report_html_container iframe {
    background-color: #ffffff !important;
    width: 100% !important;
    min-height: 600px !important;
    border: none !important;
}

/* Poprawka dla samego elementu HTML */
#report_html_container > div {
    background-color: #ffffff !important;
}

/* Pasek przewijania dla kontenera HTML */
#report_html_container::-webkit-scrollbar {
    width: 10px !important;
}

#report_html_container::-webkit-scrollbar-track {
    background: #27272a !important;
    border-radius: 5px !important;
}

#report_html_container::-webkit-scrollbar-thumb {
    background: #52525b !important;
    border-radius: 5px !important;
}

#report_html_container::-webkit-scrollbar-thumb:hover {
    background: #667eea !important;
}

hr {
    margin: 15px 0 !important;
}
"""

def run_gradio_admin_interface(port):
    """
    Uruchamia interfejs Gradio na określonym porcie.
    """
    handle_port_conflict(port)
    
    open_firewalld_port(port)
    print(f"\n  🌐  Uruchamianie Gradio:  http://{get_external_ip()}:{port}")
    
    admin_interface.launch(
        server_name="0.0.0.0", 
        server_port=port, 
        share=False,
        css=custom_css
    )
    
    print(f"")
    close_firewalld_port(port)
