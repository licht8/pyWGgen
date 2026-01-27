#!/usr/bin/env python3
"""
Testy jednostkowe menedżera portów WireGuard.

Moduł testuje rozwiązywanie konfliktów portów:
- Wykrywanie procesów na portach 51820 (WireGuard), 7860 (Gradio)
- Obsługa interaktywna (kill/exit/restart)
- Sprawdzanie psutil.net_connections()
- Graceful degradation dla błędów i wyjątków
"""

import pytest
import sys
import os
from unittest.mock import patch, Mock, MagicMock

# Dodajemy ścieżkę do projektu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyWGgen.modules.port_manager import handle_port_conflict

class TestPortManager:
    
    @patch('builtins.input', side_effect=['3'])  # Wybór "exit"
    @patch('psutil.net_connections', return_value=[MagicMock(laddr=MagicMock(port=51820), pid=1234)])
    @patch('psutil.Process')
    def test_handle_port_conflict_exit(self, mock_process, mock_connections, mock_input):
        """Test wyjścia do menu bez zabijania procesu."""
        mock_process.return_value.name.return_value = "python3"
        
        result = handle_port_conflict(51820)
        
        assert result == "exit"

    @patch('builtins.input', return_value='2')  # Wybór "restart"
    @patch('psutil.net_connections', return_value=[])
    def test_handle_port_conflict_restart_port_free(self, mock_connections, mock_input):
        """Test ponownego sprawdzenia - port wolny."""
        result = handle_port_conflict(51820)
        
        assert result == "ok"

    @patch('builtins.input', return_value='4')  # Nieprawidłowy wybór
    @patch('psutil.net_connections', return_value=[])
    def test_handle_port_conflict_invalid_choice(self, mock_connections, mock_input):
        """Test nieprawidłowego wyboru użytkownika."""
        result = handle_port_conflict(51820)
        
        assert result == "ok"

    @patch('psutil.net_connections', return_value=[])  # Port wolny
    def test_handle_port_conflict_port_free(self, mock_connections):
        """Test gdy port jest wolny od początku."""
        result = handle_port_conflict(51820)
        
        assert result == "ok"

    @patch('psutil.net_connections')
    def test_handle_port_conflict_exception(self, mock_connections):
        """Test obsługi wyjątków psutil."""
        mock_connections.side_effect = Exception("Test error")
        
        with patch('builtins.input'):
            result = handle_port_conflict(51820)
            
        assert result == "exit"

    @patch('builtins.input', side_effect=['1', '3'])  # Najpierw kill, potem exit
    @patch('psutil.net_connections', return_value=[MagicMock(laddr=MagicMock(port=51820), pid=None)])
    def test_handle_port_conflict_no_pid(self, mock_connections, mock_input):
        """Test braku PID procesu na porcie."""
        result = handle_port_conflict(51820)
        
        assert result == "exit"
