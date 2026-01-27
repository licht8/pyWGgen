#!/usr/bin/env python3
"""
Testy jednostkowe zakładki AI Diagnostics w interfejsie Gradio.

Moduł testuje implementację UI diagnostyki AI:
- Obecność pliku i kluczowych importów
- Strukturę funkcji (formatowanie, diagnostyka, tab)
- Komponenty Gradio (Button, Markdown, Accordion)
- Event handlers (click)
- Ikony statusów (🟢/🔴)
- Pipeline diagnostyczny (collect→save→analyze)
"""

import pytest
import os
from pathlib import Path
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestAIDiagnosticsTab:
    """Testy jednostkowe zakładki diagnostyki AI."""

    MAIN_FILE = 'gradio_admin/tabs/ai_diagnostics_tab.py'

    def test_file_exists(self):
        """Test istnienia pliku."""
        assert os.path.exists(self.MAIN_FILE)

    def test_imports_present(self):
        """Test obecności kluczowych importów."""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'gradio as gr', 'collect_all_data', 'analyze_with_ai', 
            'save_json_log', 'check_ollama', 'settings'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Brakuje: {imp}"

    def test_internal_functions(self):
        """Test obecności głównych funkcji."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'def format_diagnostics_summary(data: dict)' in content
        assert 'def run_diagnostics():' in content
        assert 'def ai_diagnostics_tab():' in content

    def test_gradio_components(self):
        """Test komponentów Gradio."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'gr.Button' in content
        assert 'gr.Markdown' in content

    def test_event_handlers(self):
        """Test handlerów zdarzeń."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'run_btn.click' in content
        assert 'refresh_btn.click' in content

    def test_status_icons(self):
        """Test ikon statusów."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert '"🟢" if nat.get("ok")' in content
        assert 'else "🔴"' in content
        assert '"🟢" if fw_status' in content

    def test_diagnostics_pipeline(self):
        """Test pipeline'u diagnostycznego."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'collect_all_data()' in content
        assert 'save_json_log(data' in content
        assert 'analyze_with_ai(data)' in content
        assert 'check_ollama(' in content

    def test_format_summary_content(self):
        """Test formatowania podsumowania diagnostycznego."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert '## 🚀 Diagnostyka VPN' in content
        assert 'fw.get("active", "nieznany")' in content
        assert 'data.get("health"' in content
        assert 'settings.OLLAMA_HOST' in content

    def test_buttons_labels(self):
        """Test etykiet przycisków."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert '"Uruchom diagnostykę"' in content
        assert '"Odśwież"' in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
