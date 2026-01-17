#!/usr/bin/env python3
# gradio_admin/main_interface.py

import gradio as gr
from gradio_admin.tabs.create_user_tab import create_user_tab
from gradio_admin.tabs.manage_user_tab import manage_user_tab
from gradio_admin.tabs.statistics_tab import statistics_tab
from gradio_admin.tabs.ollama_chat_tab import ollama_chat_tab
from gradio_admin.tabs.ai_diagnostics_tab import ai_diagnostics_tab
from gradio_admin.tabs.ai_report_tab import ai_report_tab

# Creating the interface
with gr.Blocks(title="pyWGgen - VPN Manager") as admin_interface:
    gr.Markdown("""
    # 🛡️ pyWGgen - WireGuard VPN Manager
    
    Управление VPN сервером с AI ассистентом
    """)
    
    with gr.Tab(label="🌱 Create"):
        create_user_tab()
    
    with gr.Tab(label="🛠️ Manage"):
        manage_user_tab()
    
    with gr.Tab(label="🔍 Statistics"):
        statistics_tab()
    
    with gr.Tab(label="🚀 AI Diagnostics"):
        ai_diagnostics_tab()
    
    with gr.Tab(label="💬 AI Chat"):
        ollama_chat_tab()
    
    with gr.Tab(label="📄 AI Report"):
        ai_report_tab()
