#!/usr/bin/env python3
# gradio_admin/main_interface.py

import gradio as gr
from gradio_admin.tabs.create_user_tab import create_user_tab
from gradio_admin.tabs.manage_user_tab import manage_user_tab
from gradio_admin.tabs.statistics_tab import statistics_tab
from gradio_admin.tabs.ollama_chat_tab import ollama_chat_tab
from gradio_admin.tabs.ai_diagnostics_tab import ai_diagnostics_tab
from gradio_admin.tabs.ai_report_tab import ai_report_tab

# Tworzenie interfejsu
with gr.Blocks(title="pyWGgen - Menedżer VPN") as admin_interface:
    gr.Markdown("""
    # 🛡️ pyWGgen - Menedżer VPN WireGuard
    
    Zarządzanie serwerem VPN z asystentem AI
    """)
    
    with gr.Tab(label="🌱 Tworzenie"):
        create_user_tab()
    
    with gr.Tab(label="🛠️ Zarządzanie"):
        manage_user_tab()
    
    with gr.Tab(label="📊 Statystyki"):
        statistics_tab()
    
    with gr.Tab(label="🚀 Diagnostyka AI"):
        ai_diagnostics_tab()
    
    with gr.Tab(label="💬 Chat AI"):
        ollama_chat_tab()
    
    with gr.Tab(label="📄 Raport AI"):
        ai_report_tab()
