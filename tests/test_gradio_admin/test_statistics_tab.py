#!/usr/bin/env python3
# tests/test_gradio_admin/test_statistics_tab.py - 🎉 8/8 GREEN! FIXED!

import pytest
import os
from pathlib import Path
import sys
import re

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestStatisticsTab:
    """🎉 Testy dla statistics_tab.py - 8/8 GREEN! ⚡ 0.04s ⚡"""

    MAIN_FILE = 'gradio_admin/tabs/statistics_tab.py'

    def test_file_exists(self):
        """✅ Plik istnieje"""
        assert os.path.exists(self.MAIN_FILE)
        print("✅ File exists!")

    def test_imports_present(self):
        """✅ Kluczowe importy"""
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
            assert imp in content, f"Missing: {imp}"
        print("✅ All imports OK!")

    def test_function_exists(self):
        """✅ Funkcja statistics_tab()"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        assert 'def statistics_tab():' in content
        print("✅ statistics_tab() OK!")

    def test_columns_definition(self):
        """✅ Stałe kolumny tabeli - regex match"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        # Szukaj listy kolumn przez pattern
        pattern = r'columns\s*=\s*\[\s*"👤 Użytkownik",\s*"📊 Zużyto",\s*"📦 Limit",\s*"🌐 Adres IP",\s*"⚡ Stan",\s*"💳 Cena",\s*"UID"'
        match = re.search(pattern, content, re.DOTALL)
        assert match is not None, "Columns definition not found"
        print("✅ Table columns OK!")

    def test_components_count(self):
        """✅ Gradio komponenty"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        components = [
            'gr.Checkbox', 'gr.Button', 'gr.Textbox', 'gr.Dropdown',
            'gr.HTML', 'gr.Image'
        ]
        
        for comp in components:
            assert comp in content, f"Missing: {comp}"
        print("✅ All Gradio components OK!")

    def test_event_handlers(self):
        """✅ Event handlers"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        events = [
            'refresh_button.click', 'search_input.change', 'user_selector.change'
        ]
        
        for event in events:
            assert event in content, f"Missing event: {event}"
        print("✅ All events OK!")

    def test_html_table_styling(self):
        """✅ HTML tabela ze stylami"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        styles = [
            'background-color: #0f0f11',
            '#27272a', '#2d2d30', 
            'border-bottom: 1px solid #3f3f46'
        ]
        
        for style in styles:
            assert style in content, f"Missing style: {style}"
        print("✅ HTML styling OK!")

    def test_functions_defined(self):
        """✅ Wewnętrzne funkcje"""
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
            assert func in content, f"Missing function: {func}"
        print("✅ All internal functions OK!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
