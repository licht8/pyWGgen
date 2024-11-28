#!/usr/bin/env python3
# modules/gradio_utils.py

import os
import subprocess
from gradio_admin.main_interface import admin_interface
from modules.project_status import get_external_ip

from firewall_utils import open_firewalld_port, close_firewalld_port, handle_port_conflict

def run_gradio_admin_interface(port=7860):
    """Запускает интерфейс Gradio на указанном порту."""
    #check_and_open_port(port)
    handle_port_conflict(port)
    open_firewalld_port(port)
    print(f" 🌐 Запуск Gradio интерфейса на http://{get_external_ip()}:{port}")
    admin_interface.launch(server_name="0.0.0.0", server_port=port, share=False)
close_firewalld_port(port)
