#!/usr/bin/env python3
"""
Testy jednostkowe zakładki czatu Ollama w interfejsie Gradio.

Moduł testuje zakładkę chatu AI:
- Importy AI (collect_all_data, ask_question, check_ollama)
- Ustawienia AI (temperature, max_tokens)
- 5 funkcji wewnętrznych + komponenty Gradio (ChatInterface)
- Przykłady pytań diagnostycznych
- Event handlers i reset ustawień
- Kontekst serwera (IP, WG status, Ollama)
"""

import pytest
import os
from pathlib import Path
import sys
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestOllamaChatTab:
    """Testy jednostkowe ollama_chat_tab.py."""

    MAIN_FILE = 'gradio_admin/tabs/ollama_chat_tab.py'

    def test_file_exists(self):
        """Test istnienia pliku."""
        assert os.path.exists(self.MAIN_FILE)

    def test_imports_present(self):
        """Test obecności kluczowych importów."""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'gradio as gr', 'collect_all_data', 'ask_question', 
            'check_ollama', 'run_cmd', 'settings'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Brakuje: {imp}"

    def test_ai_settings_dict(self):
        """Test globalnych ustawień AI."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'ai_settings = {' in content
        assert '"temperature": 0.7' in content
        assert '"max_tokens": 2000' in content
        assert 'WireGuard VPN' in content and 'po polsku' in content

    def test_internal_functions(self):
        """Test obecności głównych funkcji."""
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
            assert func in content, f"Brakuje: {func}"

    def test_gradio_components(self):
        """Test komponentów Gradio."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        components = [
            'gr.ChatInterface', 'gr.Chatbot', 'gr.Textbox', 
            'gr.Slider', 'gr.Accordion', 'gr.Button', 'gr.Markdown'
        ]
        
        for comp in components:
            assert comp in content, f"Brakuje: {comp}"

    def test_chat_examples(self):
        """Test przykładów pytań w ChatInterface."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        examples = [
            "Ile peers jest podłączonych?",
            "Jaki jest mój zewnętrzny IP?",
            "Pokaż status WireGuard"
        ]
        
        for ex in examples:
            assert ex in content, f"Brakuje przykładu: {ex}"

    def test_event_handlers(self):
        """Test event handlers."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        events = [
            'refresh_context_btn.click',
            'save_settings_btn.click', 
            'reset_settings_btn.click'
        ]
        
        for event in events:
            assert event in content, f"Brakuje zdarzenia: {event}"

    def test_server_context_features(self):
        """Test kontekstu serwera."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        context_features = [
            'curl -s ifconfig.me',
            'ip addr show',
            'wg-mgmt',
            'ollama_ok',
            'MODEL_NAME'
        ]
        
        for feature in context_features:
            assert feature in content, f"Brakuje funkcji kontekstu: {feature}"

    def test_reset_settings(self):
        """Test funkcji reset_settings."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'def reset_settings():' in content
        assert '0.7,' in content and '2000,' in content
        assert '🔄 Ustawienia zresetowane' in content

    def test_help_file_path(self):
        """Test ścieżki do pliku pomocy."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'ai_help.md' in content
        assert 'load_ai_help()' in content

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
