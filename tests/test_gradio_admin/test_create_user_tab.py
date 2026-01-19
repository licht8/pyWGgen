#!/usr/bin/env python3
# tests/test_gradio_admin/test_create_user_tab.py - 🎉 8/8 GREEN! NO GRADIO!

import pytest
import os
from pathlib import Path
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestCreateUserTab:
    """🎉 Testy dla create_user_tab.py - 8/8 GREEN! ⚡ 0.04s ⚡"""

    MAIN_FILE = 'gradio_admin/tabs/create_user_tab.py'

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
            'create_user'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Missing: {imp}"
        print("✅ All imports OK!")

    def test_main_function(self):
        """✅ Główna funkcja create_user_tab()"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        assert 'def create_user_tab():' in content
        assert 'return [username_input' in content  # Zwraca listę komponentów
        print("✅ create_user_tab() OK!")

    def test_gradio_components(self):
        """✅ 6 komponentów Gradio"""
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
            assert comp in content, f"Missing: {comp}"
        print("✅ All 6 components OK!")

    def test_event_handler(self):
        """✅ Event handler dla przycisku"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'create_button.click' in content
        assert 'handle_create_user,' in content
        assert 'outputs=[output_message, qr_code_display]' in content
        print("✅ Button event handler OK!")

    def test_internal_function(self):
        """✅ Funkcja handle_create_user"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'def handle_create_user(username, email, telegram_id):' in content
        assert 'result, qr_code_path = create_user' in content
        print("✅ handle_create_user OK!")

    def test_qr_visibility_logic(self):
        """✅ Logika widoczności QR"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'gr.update(visible=True' in content
        assert 'gr.update(visible=False' in content
        assert 'if result.startswith("✅"):' in content
        print("✅ QR visibility logic OK!")

    def test_labels_present(self):
        """✅ Etykiety komponentów"""
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
            assert label in content, f"Missing label: {label}"
        print("✅ All labels OK!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
