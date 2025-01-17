#!/usr/bin/env python3
# modules/gradio_utils.py

import os
import subprocess
from gradio_admin.main_interface import admin_interface
from modules.firewall_utils import open_firewalld_port, close_firewalld_port, handle_port_conflict, get_external_ip

def run_gradio_admin_interface(port):
    """Launches the Gradio interface on the specified port."""
    handle_port_conflict(port)
    
    open_firewalld_port(port)
    print(f"\n  🌐  Launching Gradio:  http://{get_external_ip()}:{port}")
    admin_interface.launch(server_name="0.0.0.0", server_port=port, share=False)
    print(f"")
    close_firewalld_port(port)
