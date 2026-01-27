#!/usr/bin/env python3
"""
Testy jednostkowe modułu utils dla AI Assistant WireGuard VPN.

Moduł testuje funkcje pomocnicze:
- Tworzenie katalogów logów AI
- Bezpieczne wykonywanie poleceń systemowych (timeout)
- Sprawdzanie dostępności Ollama (HTTP 200)
- Zapisywanie/odczyt logów JSON z timestamp
- Znajdowanie najnowszego pliku logu
"""

import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
import subprocess
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_assistant.utils import (
    get_log_dir, run_cmd, check_ollama, save_json_log, 
    load_json_log, get_latest_log
)


class TestUtils:
    """Testy jednostkowe modułu utils."""

    @patch('ai_assistant.utils.settings.AI_ASSISTANT_LOG_DIR', '/tmp/ai_logs')
    @patch('pathlib.Path.mkdir')
    def test_get_log_dir(self, mock_mkdir):
        """Test tworzenia katalogu logów."""
        result = get_log_dir()
        assert result == Path('/tmp/ai_logs')
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch('subprocess.run')
    def test_run_cmd_success(self, mock_run):
        """Test pomyślnego wykonania polecenia."""
        mock_run.return_value = Mock(stdout="test output", stderr="")
        result = run_cmd("ls")
        assert result == "test output"

    @patch('subprocess.run', side_effect=subprocess.TimeoutExpired("cmd", timeout=1))
    def test_run_cmd_timeout(self, mock_run):
        """Test timeout polecenia."""
        result = run_cmd("sleep 60", timeout=1)
        assert "Przekroczono czas po 1s" in result

    @patch('subprocess.run', side_effect=Exception("Test error"))
    def test_run_cmd_error(self, mock_run):
        """Test błędu wykonania polecenia."""
        result = run_cmd("invalid")
        assert "Błąd: Test error" in result

    @patch('requests.get')
    def test_check_ollama_success(self, mock_get):
        """Test dostępności Ollama - sukces."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        result = check_ollama("http://localhost:11434")
        assert result is True

    @patch('requests.get', side_effect=Exception("Connection error"))
    def test_check_ollama_fail(self, mock_get):
        """Test niedostępności Ollama."""
        result = check_ollama("http://badhost:11434")
        assert result is False

    @patch('ai_assistant.utils.datetime')
    @patch('ai_assistant.utils.get_log_dir')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_json_log(self, mock_file, mock_get_log_dir, mock_datetime):
        """Test zapisywania logu JSON z timestamp."""
        mock_get_log_dir.return_value = Path('/tmp/logs')
        mock_datetime.now.return_value.strftime.return_value = "20260118_150000"
        
        data = {"test": "data"}
        result = save_json_log(data, prefix="diag")
        assert '/diag_20260118_150000.json' in result
        mock_file.assert_called_once()

    @patch('builtins.open')
    def test_load_json_log_success(self, mock_file):
        """Test odczytu poprawnego logu JSON."""
        mock_content = '{"key": "value"}'
        mock_file.return_value.__enter__.return_value.read.return_value = mock_content
        result = load_json_log("/tmp/test.json")
        assert result == {"key": "value"}

    @patch('builtins.open', side_effect=FileNotFoundError("No file"))
    def test_load_json_log_missing(self, mock_file):
        """Test odczytu nieistniejącego pliku."""
        result = load_json_log("/tmp/missing.json")
        assert result == {"error": "No file"}

    @patch('ai_assistant.utils.get_log_dir')
    def test_get_latest_log_exists(self, mock_get_log_dir):
        """Test znajdowania najnowszego logu."""
        mock_log_dir = MagicMock()
        mock_get_log_dir.return_value = mock_log_dir
        
        mock_log_dir.glob.return_value = [
            '/tmp/logs/diag_20260118_140000.json',
            '/tmp/logs/diag_20260118_150000.json'
        ]
        
        result = get_latest_log("diag")
        assert result == '/tmp/logs/diag_20260118_150000.json'
        mock_log_dir.glob.assert_called_once_with('diag_*.json')

    @patch('ai_assistant.utils.get_log_dir')
    def test_get_latest_log_none(self, mock_get_log_dir):
        """Test braku logów."""
        mock_get_log_dir.return_value.glob.return_value = []
        result = get_latest_log("diag")
        assert result is None

    @patch('ai_assistant.utils.settings.AI_ASSISTANT_LOG_DIR', '/tmp/test_logs')
    def test_get_log_dir_real(self, tmp_path):
        """Test rzeczywistego katalogu logów."""
        result = get_log_dir()
        assert str(result) == '/tmp/test_logs'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
