#!/usr/bin/env python3
"""
Testy jednostkowe zakładki tworzenia użytkownika w interfejsie Gradio.

Moduł testuje implementację UI tworzenia użytkownika:
- Importy Gradio i create_user
- 6 komponentów UI (Textbox, Button, Image)
- Event handler przycisku tworzenia
- Funkcja handle_create_user
- Logika widoczności kodu QR
- Etykiety i lokalizacja PL
"""

import pytest
import os
from pathlib import Path
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestCreateUserTab:
    """Testy jednostkowe zakładki tworzenia użytkownika."""

    MAIN_FILE = 'gradio_admin/tabs/create_user_tab.py'

    def test_file_exists(self):
        """Test istnienia pliku."""
        assert os.path.exists(self.MAIN_FILE)

    def test_imports_present(self):
        """Test obecności kluczowych importów."""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'gradio as gr', 
            'create_user'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Brakuje: {imp}"

    def test_main_function(self):
        """Test głównej funkcji create_user_tab()."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        assert 'def create_user_tab():' in content
        assert 'return [username_input' in content

    def test_gradio_components(self):
        """Test 6 komponentów Gradio."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        components = [
            'username_input = gr.Textbox',
            'email_input = gr.Textbox', 
            'telegram_input = gr.Textbox',
            'create_button = gr.Button',
            'output_message = gr.Textbox',
            'qr_code_display = gr.Image'
        ]
        
        for comp in components:
            assert comp in content, f"Brakuje: {comp}"

    def test_event_handler(self):
        """Test handlera zdarzenia przycisku."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'create_button.click' in content
        assert 'handle_create_user,' in content
        assert 'outputs=[output_message, qr_code_display]' in content

    def test_internal_function(self):
        """Test funkcji handle_create_user."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'def handle_create_user(username, email, telegram_id):' in content
        assert 'result, qr_code_path = create_user' in content

    def test_qr_visibility_logic(self):
        """Test logiki widoczności QR."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'gr.update(visible=True' in content
        assert 'gr.update(visible=False' in content
        assert 'if result.startswith("✅"):' in content

    def test_labels_present(self):
        """Test etykiet komponentów."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        labels = [
            'label="Nazwa użytkownika"',
            'label="Email (opcjonalnie)"', 
            'label="ID Telegram (opcjonalnie)"',
            'label="Wynik"',
            'label="Kod QR"'
        ]
        
        for label in labels:
            assert label in content, f"Brakuje etykiety: {label}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
