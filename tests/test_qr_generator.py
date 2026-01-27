#!/usr/bin/env python3
"""
Testy jednostkowe generatora kodów QR dla konfiguracji WireGuard.

Moduł testuje generowanie kodów QR:
- Podstawowa generacja z pyqrcode.create()
- Tworzenie QR z rzeczywistych konfiguracji WireGuard
- Obsługa nieistniejących ścieżek zapisu
- Mockowanie biblioteki pyqrcode i systemu plików
"""

import pytest
import sys
import os
from unittest.mock import patch, Mock
import tempfile

# Dodajemy ścieżkę do projektu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyWGgen.modules.qr_generator import generate_qr_code
from pyWGgen.modules.keygen import generate_private_key
from pyWGgen.modules.client_config import create_client_config

class TestQRGenerator:
    
    @patch('pyqrcode.create')
    @patch('builtins.open', new_callable=Mock)
    def test_generate_qr_code_success(self, mock_file, mock_pyqrcode):
        """Test poprawnej generacji kodu QR."""
        mock_qr = Mock()
        mock_pyqrcode.return_value = mock_qr
        
        test_config = "[Interface]\nPrivateKey = testkey\n[Peer]\nPublicKey = testpub"
        temp_path = "/tmp/test_qr.png"
        
        generate_qr_code(test_config, temp_path)
        
        mock_pyqrcode.assert_called_once_with(test_config)
        mock_qr.png.assert_called_once_with(temp_path, scale=6)

    @patch('pyqrcode.create')
    def test_generate_qr_code_real_config(self, mock_pyqrcode):
        """Test z rzeczywistą konfiguracją WireGuard."""
        private_key = generate_private_key()
        server_pubkey = generate_private_key()
        config_data = create_client_config(
            private_key=private_key,
            address="10.0.0.2/32",
            dns_servers="1.1.1.1",
            server_public_key=server_pubkey.decode(),
            preshared_key=generate_private_key(),
            endpoint="test.server:51820"
        )
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            qr_path = tmp_file.name
            
        try:
            generate_qr_code(config_data, qr_path)
            mock_pyqrcode.assert_called_once_with(config_data)
        finally:
            os.unlink(qr_path)

    def test_generate_qr_code_invalid_path(self):
        """Test niedostępnej ścieżki zapisu."""
        test_data = "test config"
        invalid_path = "/root/inexistent/dir/qr.png"
        
        with patch('pyqrcode.create') as mock_create:
            generate_qr_code(test_data, invalid_path)
        
        mock_create.assert_called_once()
