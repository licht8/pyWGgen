#!/usr/bin/env python3
# gradio_admin/main_interface.py

import gradio as gr
from gradio_admin.tabs.create_user_tab import create_user_tab
from gradio_admin.tabs.manage_user_tab import manage_user_tab
from gradio_admin.tabs.statistics_tab import statistics_tab
from gradio_admin.tabs.ollama_chat_tab import ollama_chat_tab

# Creating the interface
with gr.Blocks() as admin_interface:
    with gr.Tab(label="🌱 Create"):
        create_user_tab()
    
    with gr.Tab(label="🛠️ Manage"):
        manage_user_tab()
    
    with gr.Tab(label="🔍 Statistics"):
        statistics_tab()
    
    '''
    with gr.Tab(label="🤖 Chat with AI"):
        ollama_chat_tab()
    '''


    # Uncomment for additional features
    # with gr.Tab(label="🖥️ Command Line"):
        # command_line_tab()
