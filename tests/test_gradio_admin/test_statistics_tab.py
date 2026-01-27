#!/usr/bin/env python3
"""
Testy jednostkowe zakładki statystyk WireGuard VPN w interfejsie Gradio.

Moduł testuje zakładkę statystyk z tabelą pandas:
- Importy (pandas, load_user_records, format_user_info)
- Definicja kolumn tabeli z emoji
- Komponenty Gradio (Checkbox, HTML tabela, Image)
- Event handlers (refresh, search, user_selector)
- HTML styling tabeli
- 6 funkcji wewnętrznych (df_to_html, refresh_table)
"""

import pytest
import os
from pathlib import Path
import sys
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestStatisticsTab:
    """Testy jednostkowe statistics_tab.py."""

    MAIN_FILE = 'gradio_admin/tabs/statistics_tab.py'

    def test_file_exists(self):
        """Test istnienia pliku."""
        assert os.path.exists(self.MAIN_FILE)

    def test_imports_present(self):
        """Test obecności kluczowych importów."""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'gradio as gr',
            'pandas as pd', 
            'load_user_records',
            'format_time',
            'update_table',
            'format_user_info',
            'show_user_info',
            'update_traffic_data',
            'USER_DB_PATH',
            'QR_CODE_DIR'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Brakuje: {imp}"

    def test_function_exists(self):
        """Test funkcji statistics_tab()."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        assert 'def statistics_tab():' in content

    def test_columns_definition(self):
        """Test definicji kolumn tabeli."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        pattern = r'columns\s*=\s*\[\s*"👤 Użytkownik",\s*"📊 Zużyto",\s*"📦 Limit",\s*"🌐 Adres IP",\s*"⚡ Stan",\s*"💳 Cena",\s*"UID'
        match = re.search(pattern, content, re.DOTALL)
        assert match is not None, "Brak definicji kolumn"

    def test_components_count(self):
        """Test komponentów Gradio."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        components = [
            'gr.Checkbox', 'gr.Button', 'gr.Textbox', 'gr.Dropdown',
            'gr.HTML', 'gr.Image'
        ]
        
        for comp in components:
            assert comp in content, f"Brakuje: {comp}"

    def test_event_handlers(self):
        """Test event handlers."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        events = [
            'refresh_button.click', 'search_input.change', 'user_selector.change'
        ]
        
        for event in events:
            assert event in content, f"Brakuje zdarzenia: {event}"

    def test_html_table_styling(self):
        """Test stylizacji HTML tabeli."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        styles = [
            'background-color: #0f0f11',
            '#27272a', '#2d2d30', 
            'border-bottom: 1px solid #3f3f46'
        ]
        
        for style in styles:
            assert style in content, f"Brakuje stylu: {style}"

    def test_functions_defined(self):
        """Test wewnętrznych funkcji."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        functions = [
            'def get_initial_data():',
            'def df_to_html(df):', 
            'def refresh_table(show_inactive):',
            'def search_table(query):',
            'def find_qr_code(username):',
            'def display_user_info(selected_user):'
        ]
        
        for func in functions:
            assert func in content, f"Brakuje funkcji: {func}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
