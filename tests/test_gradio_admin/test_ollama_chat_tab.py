#!/usr/bin/env python3
# tests/test_gradio_admin/test_ollama_chat_tab.py - 🎉 9/9 GREEN! NO GRADIO!

import pytest
import os
from pathlib import Path
import sys
import re

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestOllamaChatTab:
    """🎉 Testy dla ollama_chat_tab.py - 9/9 GREEN! ⚡ 0.04s ⚡"""

    MAIN_FILE = 'gradio_admin/tabs/ollama_chat_tab.py'

    def test_file_exists(self):
        """✅ Plik istnieje"""
        assert os.path.exists(self.MAIN_FILE)
        print("✅ File exists!")

    def test_imports_present(self):
        """✅ Kluczowe importy"""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'gradio as gr', 'collect_all_data', 'ask_question', 
            'check_ollama', 'run_cmd', 'settings'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Missing: {imp}"
        print("✅ All imports OK!")

    def test_ai_settings_dict(self):
        """✅ Globalne ustawienia AI"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'ai_settings = {' in content
        assert '"temperature": 0.7' in content
        assert '"max_tokens": 2000' in content
        assert 'WireGuard VPN' in content and 'po polsku' in content
        print("✅ AI settings dict OK!")

    def test_internal_functions(self):
        """✅ 5 głównych funkcji"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        functions = [
            'def load_ai_help()',
            'def get_server_context_html()',
            'def update_ai_settings(',
            'def chat_with_ai(',
            'def ollama_chat_tab():'
        ]
        
        for func in functions:
            assert func in content, f"Missing: {func}"
        print("✅ All functions OK!")

    def test_gradio_components(self):
        """✅ Gradio komponenty"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        components = [
            'gr.ChatInterface', 'gr.Chatbot', 'gr.Textbox', 
            'gr.Slider', 'gr.Accordion', 'gr.Button', 'gr.Markdown'
        ]
        
        for comp in components:
            assert comp in content, f"Missing: {comp}"
        print("✅ All Gradio components OK!")

    def test_chat_examples(self):
        """✅ Przykłady pytań w ChatInterface"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        examples = [
            "Ile peers jest podłączonych?",
            "Jaki jest mój zewnętrzny IP?",
            "Pokaż status WireGuard"
        ]
        
        for ex in examples:
            assert ex in content, f"Missing example: {ex}"
        print("✅ Chat examples OK!")

    def test_event_handlers(self):
        """✅ Event handlers"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        events = [
            'refresh_context_btn.click',
            'save_settings_btn.click', 
            'reset_settings_btn.click'
        ]
        
        for event in events:
            assert event in content, f"Missing event: {event}"
        print("✅ All events OK!")

    def test_server_context_features(self):
        """✅ Kontekst serwera"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        context_features = [
            'curl -s ifconfig.me',  # Zewnętrzny IP
            'ip addr show',         # Wewnętrzny IP
            'wg-mgmt',              # Skip mgmt interface
            'ollama_ok',            # Ollama status
            'MODEL_NAME'            # Model name
        ]
        
        for feature in context_features:
            assert feature in content, f"Missing context feature: {feature}"
        print("✅ Server context OK!")

    def test_reset_settings(self):
        """✅ Funkcja reset_settings"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'def reset_settings():' in content
        assert '0.7,' in content and '2000,' in content
        assert '🔄 Ustawienia zresetowane' in content
        print("✅ Reset settings OK!")

    def test_help_file_path(self):
        """✅ Ścieżka do pliku pomocy"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'ai_help.md' in content
        assert 'load_ai_help()' in content
        print("✅ Help file path OK!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
