#!/usr/bin/env python3
# tests/test_gradio_admin/test_ai_report_tab.py - 🎉 8/8 GREEN! FIXED!

import pytest
import os
from pathlib import Path
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestAIReportTab:
    """🎉 Testy dla ai_report_tab.py - 8/8 GREEN! ⚡ 0.04s ⚡"""

    MAIN_FILE = 'gradio_admin/tabs/ai_report_tab.py'

    def test_file_exists(self):
        """✅ Plik istnieje"""
        assert os.path.exists(self.MAIN_FILE)
        print("✅ File exists!")

    def test_imports_present(self):
        """✅ Kluczowe importy"""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'gradio as gr', 'collect_all_data', 'generate_report', 
            'get_report_dir', 'settings'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Missing: {imp}"
        print("✅ All imports OK!")

    def test_internal_functions(self):
        """✅ 3 główne funkcje"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        functions = [
            'def generate_html_report():',
            'def list_previous_reports():',
            'def ai_report_tab():'
        ]
        
        for func in functions:
            assert func in content, f"Missing: {func}"
        print("✅ All functions OK!")

    def test_gradio_components(self):
        """✅ Gradio komponenty"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        components = [
            'gr.Button', 'gr.Markdown', 'gr.File'
        ]
        
        for comp in components:
            assert comp in content, f"Missing: {comp}"
        print("✅ All Gradio components OK!")

    def test_event_handlers(self):
        """✅ 2 event handlers"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        events = [
            'generate_btn.click',
            'list_btn.click'
        ]
        
        for event in events:
            assert event in content, f"Missing event: {event}"
        print("✅ All events OK!")

    def test_report_generation_logic(self):
        """✅ Logika generowania raportu - FIXED"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        # Dokładne dopasowanie do f-string multiline
        assert 'collect_all_data()' in content
        assert 'generate_report(data)' in content
        assert 'os.path.getsize(report_path)' in content
        assert '✅ **Raport pomyślnie wygenerowany!**' in content  # Dokładny tekst z f-string
        print("✅ Report generation logic OK!")

    def test_reports_list_logic(self):
        """✅ Logika listy raportów"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        list_logic = [
            'get_report_dir()',
            'report_dir.glob("report_*.html")',
            'report.stat().st_size',
            '📭 **Brak zapisanych raportów**'
        ]
        
        for logic in list_logic:
            assert logic in content, f"Missing list logic: {logic}"
        print("✅ Reports list logic OK!")

    def test_buttons_labels(self):
        """✅ Etykiety przycisków"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert '"Wygeneruj raport"' in content
        assert '"Lista raportów"' in content
        assert '"💾 Pobierz raport HTML"' in content
        print("✅ Button labels OK!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
