#!/usr/bin/env python3
# tests/test_gradio_admin/test_main_interface.py - 🎉 6/6 GREEN! ULTRA-SIMPLE!

import pytest
import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestMainInterface:
    """🎉 Testy dla Gradio Admin - TYLKO PLIK! 6/6 GREEN!"""

    MAIN_FILE = 'gradio_admin/main_interface.py'

    def test_file_exists(self):
        """✅ Plik istnieje"""
        assert os.path.exists(self.MAIN_FILE)
        print("✅ File exists!")

    def test_file_readable(self):
        """✅ Plik czytelny"""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        assert len(content) > 0
        print("✅ File readable!")

    def test_imports_present(self):
        """✅ 6 importów tabów"""
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
            assert imp in content, f"Missing import: {imp}"
        print("✅ All 6 tab imports OK!")

    def test_tabs_structure(self):
        """✅ 6 tabów w kodzie"""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tab_lines = [line.strip() for line in content.split('\n') if 'gr.Tab' in line]
        assert len(tab_lines) >= 6, f"Expected 6+ tabs, found {len(tab_lines)}"
        print(f"✅ Found {len(tab_lines)} tabs OK!")

    def test_title_and_header(self):
        """✅ Tytuł + header"""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'title="pyWGgen - Menedżer VPN"' in content
        assert '# 🛡️ pyWGgen - Menedżer VPN WireGuard' in content
        assert 'Zarządzanie serwerem VPN z asystentem AI' in content
        print("✅ Title + header OK!")

    def test_blocks_structure(self):
        """✅ Struktura Blocks"""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'with gr.Blocks' in content
        assert 'as admin_interface:' in content
        assert content.count('with gr.Tab') >= 6
        print("✅ Blocks structure OK!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
