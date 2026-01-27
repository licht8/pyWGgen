#!/usr/bin/env python3
"""
Testy jednostkowe modułu firewall_utils.

Moduł testuje zarządzanie zaporą ogniową:
- Pobieranie zewnętrznego adresu IP
- Otwieranie portów firewalld (WireGuard 51820, Gradio 7860)
- Zamykanie portów firewalld
- Obsługę błędów sieciowych i subprocess
"""

import pytest
import sys
import os
from unittest.mock import patch, Mock

# Dodajemy ścieżkę do projektu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyWGgen.modules.firewall_utils import (
    get_external_ip, 
    open_firewalld_port, 
    close_firewalld_port
)

class TestFirewallUtils:
    
    def test_get_external_ip_success(self):
        """Test poprawnego pobierania zewnętrznego IP."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.getsockname.return_value = ('192.168.1.100', 12345)
            mock_socket.return_value.__enter__.return_value = mock_sock
            
            ip = get_external_ip()
            assert ip == '192.168.1.100'

    def test_get_external_ip_error(self):
        """Test obsługi błędu pobierania IP."""
        with patch('socket.socket') as mock_socket:
            mock_socket.side_effect = OSError("No network")
            ip = get_external_ip()
            assert "N/A ❌" in ip

    @patch('subprocess.run')
    @patch('builtins.print')
    @patch('builtins.input', return_value='3')  # Wybór "Powrót do menu"
    def test_open_firewalld_port(self, mock_input, mock_print, mock_subprocess):
        """Test otwierania portu firewalld."""
        mock_subprocess.return_value = Mock(returncode=0)
        
        open_firewalld_port(51820)
        
        mock_subprocess.assert_called_once()

    @patch('subprocess.run')
    @patch('builtins.print')
    def test_close_firewalld_port(self, mock_print, mock_subprocess):
        """Test zamykania portu firewalld."""
        mock_subprocess.return_value = Mock(returncode=0)
        
        close_firewalld_port(51820)
        
        mock_subprocess.assert_called_once()
