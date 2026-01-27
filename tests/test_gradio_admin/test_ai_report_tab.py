#!/usr/bin/env python3
"""
Testy jednostkowe zakładki AI Report w interfejsie Gradio.

Moduł testuje implementację UI generatora raportów:
- Obecność pliku i kluczowych importów
- Strukturę funkcji (generowanie HTML, lista raportów, tab)
- Komponenty Gradio (Button, Markdown, File)
- Event handlers (click)
- Logika generowania raportów HTML
- Lista poprzednich raportów z metadanymi
"""

import pytest
import os
from pathlib import Path
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestAIReportTab:
    """Testy jednostkowe zakładki generatora raportów AI."""

    MAIN_FILE = 'gradio_admin/tabs/ai_report_tab.py'

    def test_file_exists(self):
        """Test istnienia pliku."""
        assert os.path.exists(self.MAIN_FILE)

    def test_imports_present(self):
        """Test obecności kluczowych importów."""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'gradio as gr', 'collect_all_data', 'generate_report', 
            'get_report_dir', 'settings'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Brakuje: {imp}"

    def test_internal_functions(self):
        """Test obecności głównych funkcji."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        functions = [
            'def generate_html_report():',
            'def list_previous_reports():',
            'def ai_report_tab():'
        ]
        
        for func in functions:
            assert func in content, f"Brakuje: {func}"

    def test_gradio_components(self):
        """Test komponentów Gradio."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        components = [
            'gr.Button', 'gr.Markdown', 'gr.File'
        ]
        
        for comp in components:
            assert comp in content, f"Brakuje: {comp}"

    def test_event_handlers(self):
        """Test handlerów zdarzeń."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        events = [
            'generate_btn.click',
            'list_btn.click'
        ]
        
        for event in events:
            assert event in content, f"Brakuje zdarzenia: {event}"

    def test_report_generation_logic(self):
        """Test logiki generowania raportu."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'collect_all_data()' in content
        assert 'generate_report(data)' in content
        assert 'os.path.getsize(report_path)' in content
        assert '✅ **Raport pomyślnie wygenerowany!**' in content

    def test_reports_list_logic(self):
        """Test logiki listy raportów."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        list_logic = [
            'get_report_dir()',
            'report_dir.glob("report_*.html")',
            'report.stat().st_size',
            '📭 **Brak zapisanych raportów**'
        ]
        
        for logic in list_logic:
            assert logic in content, f"Brakuje logiki listy: {logic}"

    def test_buttons_labels(self):
        """Test etykiet przycisków."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert '"Wygeneruj raport"' in content
        assert '"Lista raportów"' in content
        assert '"💾 Pobierz raport HTML"' in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
