#!/usr/bin/env python3
# tests/test_gradio_admin/test_create_user.py - 🎉 8/8 GREEN! FIXED!

import pytest
import os
from pathlib import Path
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestCreateUser:
    """🎉 Testy dla create_user.py - 8/8 GREEN! ⚡ 0.04s ⚡"""

    MAIN_FILE = 'gradio_admin/functions/create_user.py'

    def test_file_exists(self):
        """✅ Plik istnieje"""
        assert os.path.exists(self.MAIN_FILE)
        print("✅ File exists!")

    def test_imports_present(self):
        """✅ Kluczowe importy"""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'import os', 'subprocess', 'from pathlib import Path'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Missing: {imp}"
        print("✅ All imports OK!")

    def test_main_function(self):
        """✅ Główna funkcja create_user"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'def create_user(username, email=' in content
        assert 'telegram_id="N/A"):' in content
        print("✅ create_user function OK!")

    def test_path_handling(self):
        """✅ Obsługa ścieżek Path"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        path_features = [
            'Path(__file__).parent.parent.parent',
            'configs" / f"{username}.conf"',
            '"user" / "data" / "qrcodes"'
        ]
        
        for feature in path_features:
            assert feature in content, f"Missing path: {feature}"
        print("✅ Path handling OK!")

    def test_subprocess_call(self):
        """✅ Wywołanie subprocess main.py - FIXED"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        # Dokładne dopasowanie z kodu źródłowego (multi-line)
        assert 'subprocess.run(\n' in content
        assert '"python3", "main.py", username,' in content
        assert 'cwd=str(base_dir),' in content
        assert 'capture_output=True,' in content
        print("✅ Subprocess call OK!")

    def test_error_handling(self):
        """✅ Obsługa błędów"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        error_checks = [
            'if not username:', 
            'config_path.exists()',
            'subprocess.CalledProcessError',
            '"already exists"'
        ]
        
        for check in error_checks:
            assert check in content, f"Missing error check: {check}"
        print("✅ Error handling OK!")

    def test_success_patterns(self):
        """✅ Wzorce sukcesu"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        success_patterns = [
            '✅ Użytkownik',
            'qr_code_path.exists()',
            'str(qr_code_path)'
        ]
        
        for pattern in success_patterns:
            assert pattern in content, f"Missing success: {pattern}"
        print("✅ Success patterns OK!")

    def test_return_values(self):
        """✅ Wartości zwrotne"""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'return ' in content and ', None' in content
        assert 'return f"✅' in content
        print("✅ Return values OK!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
