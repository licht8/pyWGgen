import pytest
import sys
import os
from unittest.mock import patch, Mock, MagicMock

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyWGgen.modules.port_manager import handle_port_conflict

class TestPortManager:
    
    @patch('builtins.input', side_effect=['3'])  # Выбираем "exit" вместо kill
    @patch('psutil.net_connections', return_value=[MagicMock(laddr=MagicMock(port=51820), pid=1234)])
    @patch('psutil.Process')
    def test_handle_port_conflict_exit(self, mock_process, mock_connections, mock_input):
        """Тест выхода в меню"""
        mock_process.return_value.name.return_value = "python3"
        
        result = handle_port_conflict(51820)
        
        assert result == "exit"
        print("✅ handle_port_conflict() возвращает exit!")

    @patch('builtins.input', return_value='2')  # Выбираем "restart"
    @patch('psutil.net_connections', return_value=[])
    def test_handle_port_conflict_restart_port_free(self, mock_connections, mock_input):
        """Тест повторной проверки - порт свободен"""
        result = handle_port_conflict(51820)
        
        assert result == "ok"  # Порт свободен = "ok"
        print("✅ handle_port_conflict() restart + свободный порт!")

    @patch('builtins.input', return_value='4')  # Неверный выбор
    @patch('psutil.net_connections', return_value=[])
    def test_handle_port_conflict_invalid_choice(self, mock_connections, mock_input):
        """Тест неверного выбора"""
        result = handle_port_conflict(51820)
        
        assert result == "ok"
        print("✅ handle_port_conflict() неверный ввод + свободный порт!")

    @patch('psutil.net_connections', return_value=[])  # Порт свободен
    def test_handle_port_conflict_port_free(self, mock_connections):
        """Тест свободного порта"""
        result = handle_port_conflict(51820)
        
        assert result == "ok"
        print("✅ handle_port_conflict() порт свободен!")

    @patch('psutil.net_connections')
    def test_handle_port_conflict_exception(self, mock_connections):
        """Тест обработки исключения"""
        mock_connections.side_effect = Exception("Test error")
        
        with patch('builtins.input'):
            result = handle_port_conflict(51820)
            
        assert result == "exit"
        print("✅ handle_port_conflict() ловит исключения!")

    @patch('builtins.input', side_effect=['1', '3'])  # Сначала kill, потом exit
    @patch('psutil.net_connections', return_value=[MagicMock(laddr=MagicMock(port=51820), pid=None)])
    def test_handle_port_conflict_no_pid(self, mock_connections, mock_input):
        """Тест без PID процесса"""
        result = handle_port_conflict(51820)
        
        assert result == "exit"
        print("✅ handle_port_conflict() без PID!")
