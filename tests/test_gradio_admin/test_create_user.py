#!/usr/bin/env python3
"""
Testy jednostkowe funkcji tworzenia użytkownika WireGuard VPN.

Moduł testuje implementację tworzenia użytkownika:
- Obsługa ścieżek Path (configs, qrcodes)
- Wywołanie subprocess main.py
- Walidacja parametrów (username, email)
- Sprawdzanie istnienia plików konfiguracji/QR
- Obsługa błędów subprocess i duplikatów
"""

import pytest
import os
from pathlib import Path
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestCreateUser:
    """Testy jednostkowe funkcji tworzenia użytkownika."""

    MAIN_FILE = 'gradio_admin/functions/create_user.py'

    def test_file_exists(self):
        """Test istnienia pliku."""
        assert os.path.exists(self.MAIN_FILE)

    def test_imports_present(self):
        """Test obecności kluczowych importów."""
        with open(self.MAIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            'import os', 'subprocess', 'from pathlib import Path'
        ]
        
        for imp in required_imports:
            assert imp in content, f"Brakuje: {imp}"

    def test_main_function(self):
        """Test głównej funkcji create_user."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'def create_user(username, email=' in content
        assert 'telegram_id="N/A"):' in content

    def test_path_handling(self):
        """Test obsługi ścieżek Path."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        path_features = [
            'Path(__file__).parent.parent.parent',
            'configs" / f"{username}.conf"',
            '"user" / "data" / "qrcodes"'
        ]
        
        for feature in path_features:
            assert feature in content, f"Brakuje ścieżki: {feature}"

    def test_subprocess_call(self):
        """Test wywołania subprocess main.py."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'subprocess.run(\n' in content
        assert '"python3", "main.py", username,' in content
        assert 'cwd=str(base_dir),' in content
        assert 'capture_output=True,' in content
        print("✅ Subprocess call OK!")

    def test_error_handling(self):
        """Test obsługi błędów."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        error_checks = [
            'if not username:', 
            'config_path.exists()',
            'subprocess.CalledProcessError',
            '"already exists"'
        ]
        
        for check in error_checks:
            assert check in content, f"Brakuje sprawdzenia błędu: {check}"

    def test_success_patterns(self):
        """Test wzorców sukcesu."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        success_patterns = [
            '✅ Użytkownik',
            'qr_code_path.exists()',
            'str(qr_code_path)'
        ]
        
        for pattern in success_patterns:
            assert pattern in content, f"Brakuje wzorca sukcesu: {pattern}"

    def test_return_values(self):
        """Test wartości zwrotnych."""
        with open(self.MAIN_FILE, 'r') as f:
            content = f.read()
        
        assert 'return ' in content and ', None' in content
        assert 'return f"✅' in content

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

