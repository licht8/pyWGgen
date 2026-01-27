#!/usr/bin/env python3
"""
Testy jednostkowe zakładki zarządzania użytkownikami w interfejsie Gradio.

Moduł testuje zakładkę zarządzania użytkownikami:
- Importy funkcji (delete_user, block_user, sync_users)
- Stała WG_CONFIGS_PATH
- 6 funkcji wewnętrznych + komponenty Gradio
- 6 przycisków akcji i event handlers
- Logika plików konfiguracji i parsowanie listy
- Funkcja synchronizacji katalogów
"""

import pytest
import os
from pathlib import Path
import sys
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestManageUserTab:
    """Testy jednostkowe manage_user_tab.py."""

    MAIN_FILE = 'gradio_admin/tabs/manage_user_tab.py'

    def test_file_exists(self):
        """Test istnienia pliku."""
        assert os.path.exists(self.MAIN_FILE)

    def test_imports_present(self):
        """Test obecności kluczowych importów."""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'gradio as gr', 'delete_user', 'load_user_records',
            'block_user', 'unblock_user', 'sync_users_from_config_paths'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Brakuje: {imp}"

    def test_constants(self):
        """Test stałej WG_CONFIGS_PATH."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'WG_CONFIGS_PATH = "/root/pyWGgenerator/pyWGgen/user/data/wg_configs"' in content

    def test_internal_functions(self):
        """Test obecności głównych funkcji."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        functions = [
            'def get_user_config_path(username):',
            'def handle_download_config(',
            'def manage_user_tab():',
            'def get_user_list():',
            'def handle_user_deletion(',
            'def handle_sync('
        ]
        
        for func in functions:
            assert func in content, f"Brakuje: {func}"

    def test_gradio_components(self):
        """Test komponentów Gradio."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        components = [
            'gr.Dropdown', 'gr.Button', 'gr.Textbox', 'gr.File'
        ]
        
        for comp in components:
            assert comp in content, f"Brakuje: {comp}"

    def test_buttons_present(self):
        """Test 6 przycisków akcji."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        buttons = [
            'refresh_button', 'delete_button', 'block_button',
            'unblock_button', 'download_button', 'sync_button'
        ]
        
        for btn in buttons:
            assert f'{btn} = gr.Button' in content, f"Brakuje przycisku: {btn}"

    def test_event_handlers(self):
        """Test 6 event handlers."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        events = [
            'refresh_button.click', 'delete_button.click', 'block_button.click',
            'unblock_button.click', 'sync_button.click', 'download_button.click'
        ]
        
        for event in events:
            assert event in content, f"Brakuje zdarzenia: {event}"

    def test_config_files_logic(self):
        """Test logiki plików konfiguracji."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        config_files = ['"{username}.conf"', '"{username}_local.conf"']
        for conf in config_files:
            assert conf in content, f"Brakuje konfiguracji: {conf}"

    def test_user_list_parsing(self):
        """Test parsowania listy użytkowników."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'status = user_data.get("status"' in content
        assert 'f"{username} {display_status}"' in content

    def test_sync_function_inputs(self):
        """Test funkcji synchronizacji."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'handle_sync(config_dir_str, qr_dir_str)' in content
        assert 'config_dir_input = gr.Textbox' in content
        assert 'qr_dir_input = gr.Textbox' in content

    def test_main_function(self):
        """Test głównej funkcji manage_user_tab()."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'def manage_user_tab():' in content
        assert content.count('gr.') >= 10

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
