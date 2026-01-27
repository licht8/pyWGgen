#!/usr/bin/env python3
"""
Testy jednostkowe głównego interfejsu Gradio Admin WireGuard VPN.

Moduł testuje główny plik interfejsu:
- Istnienie i czytelność pliku main_interface.py
- 6 importów zakładek (create_user, manage_user, statistics, AI)
- Strukturę 6+ tabów gr.Tab
- Tytuł i header z lokalizacją PL
- Strukturę gr.Blocks
"""

import pytest
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestMainInterface:
    """Testy jednostkowe głównego interfejsu Gradio."""

    MAIN_FILE = 'gradio_admin/main_interface.py'

    def test_file_exists(self):
        """Test istnienia pliku."""
        assert os.path.exists(self.MAIN_FILE)

    def test_file_readable(self):
        """Test czytelności pliku."""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        assert len(content) > 0

    def test_imports_present(self):
        """Test obecności 6 importów tabów."""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'create_user_tab',
            'manage_user_tab', 
            'statistics_tab',
            'ollama_chat_tab',
            'ai_diagnostics_tab',
            'ai_report_tab'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Brakuje importu: {imp}"

    def test_tabs_structure(self):
        """Test struktury 6 tabów."""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tab_lines = [line.strip() for line in content.split('\n') if 'gr.Tab' in line]
        assert len(tab_lines) >= 6, f"Oczekiwano 6+ tabów, znaleziono {len(tab_lines)}"

    def test_title_and_header(self):
        """Test tytułu i nagłówka."""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'title="pyWGgen - Menedżer VPN"' in content
        assert '# 🛡️ pyWGgen - Menedżer VPN WireGuard' in content
        assert 'Zarządzanie serwerem VPN z asystentem AI' in content

    def test_blocks_structure(self):
        """Test struktury Blocks."""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'with gr.Blocks' in content
        assert 'as admin_interface:' in content
        assert content.count('with gr.Tab') >= 6

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
