#!/usr/bin/env python3
"""
Testy jednostkowe trybu czatu AI dla diagnostyki WireGuard VPN.

Moduł testuje interaktywny chat z lokalnym AI (Ollama):
- Wyświetlanie pełnego kontekstu serwera (IP, uptime, WG status)
- Zadawanie pytań diagnostycznych z automatycznym kontekstem
- Obsługę błędów timeout/JSON i cleanup plików tymczasowych
- Tryb interaktywny z pętlą pytań
"""

import pytest
import os
import json
import sys
from unittest.mock import Mock, patch
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ai_assistant.ai_chat import (
    show_server_context,
    ask_question, 
    interactive_mode
)


class TestAIChat:
    """Testy jednostkowe dla AI Chat Mode."""

    @pytest.fixture
    def sample_server_data(self):
        """Przykładowe dane serwera."""
        return {
            "hostname": "vpn-prod-01",
            "uptime": "15 days",
            "wg_status": {
                "wg0": {"service_active": True, "peers_active": 3},
                "wg1": {"service_active": False, "peers_active": 0},
                "wg-mgmt": {"service_active": True}
            },
            "wg_active": 1,
            "wg_total": 2,
            "peers_active": 3,
            "peers_configured": 25,
            "user_peer_files": {"total": 28},
            "firewalld": {
                "active": "aktywny",
                "wg_port": "51820",
                "wg_port_open": True
            },
            "nat": {"ok": True, "reason": "MASQUERADE active"},
            "health": {"ollama_ok": True}
        }

    @patch('ai_assistant.ai_chat.run_cmd')
    def test_show_server_context_full(self, mock_run_cmd, sample_server_data, capsys):
        """Test pełnego kontekstu serwera."""
        mock_run_cmd.side_effect = [
            "203.0.113.1",           # curl ifconfig.me
            "10.66.66.1/24",         # ip addr wg0
        ]
        
        show_server_context(sample_server_data)
        captured = capsys.readouterr()
        output = captured.out
        
        assert "KONTEXT SERWERA" in output
        assert "vpn-prod-01" in output
        assert "203.0.113.1" in output
        assert "wg0" in output
        assert "3/2 aktywnych" in output or "1/2 aktywnych" in output
        assert "🟢 OK" in output

    @patch('ai_assistant.ai_chat.run_cmd', return_value="N/A")
    def test_show_server_context_minimal(self, mock_run_cmd, capsys):
        """Test minimalnych danych serwera."""
        minimal_data = {"hostname": "test-server"}
        show_server_context(minimal_data)
        captured = capsys.readouterr()
        assert "test-server" in captured.out

    @patch('ai_assistant.ai_chat.run_cmd')
    def test_ask_question_success(self, mock_run_cmd, sample_server_data):
        """Test zadawania pytania - sukces."""
        mock_run_cmd.side_effect = [
            "10.66.66.1/24",     # ip addr wg0
            "N/A",               # ip addr wg1  
            "203.0.113.1",       # curl ifconfig.me
            '{"response": "Sprawdź firewall na porcie 51820"}'  # curl ollama
        ]
        
        result = ask_question(sample_server_data, "Dlaczego brak połączeń?")
        assert "firewall" in result or "51820" in result
        assert "❌" not in result

    @patch('ai_assistant.ai_chat.run_cmd')
    def test_ask_question_json_error(self, mock_run_cmd, sample_server_data):
        """Test błędu parsowania JSON."""
        mock_run_cmd.side_effect = [
            "N/A", "N/A", "N/A",    
            '{"invalid": "json"} garbage'  
        ]
        result = ask_question(sample_server_data, "test")
        assert "Błąd parsowania" in result

    @patch('ai_assistant.ai_chat.run_cmd', return_value="Error: timeout")
    def test_ask_question_timeout(self, mock_run_cmd, sample_server_data):
        """Test timeout zapytania."""
        result = ask_question(sample_server_data, "test")
        assert "Błąd zapytania" in result

    @patch('ai_assistant.ai_chat.os.path.exists', return_value=True)
    @patch('ai_assistant.ai_chat.os.unlink')
    @patch('ai_assistant.ai_chat.run_cmd', side_effect=[
        "N/A", "N/A", "N/A", Exception("ollama timeout")
    ])
    def test_ask_question_cleanup(self, mock_run_cmd, mock_unlink, mock_exists, sample_server_data):
        """Test cleanup przy błędzie."""
        result = ask_question(sample_server_data, "test")
        mock_unlink.assert_called_once()

    @patch('ai_assistant.ai_chat.check_ollama', return_value=False)
    def test_interactive_mode_ollama_down(self, mock_check_ollama, capsys, sample_server_data):
        """Test trybu interaktywnego - Ollama offline."""
        interactive_mode(sample_server_data)
        captured = capsys.readouterr()
        assert "Ollama niedostępny" in captured.out

    @patch('ai_assistant.ai_chat.check_ollama', return_value=True)
    @patch('builtins.input', side_effect=['test', ''])  
    @patch('ai_assistant.ai_chat.ask_question')
    def test_interactive_mode_flow(self, mock_ask, mock_input, mock_check, sample_server_data, capsys):
        """Test przepływu trybu interaktywnego."""
        mock_ask.return_value = "Test OK"
        interactive_mode(sample_server_data)
        assert mock_ask.called

    def test_show_server_context_no_wg(self, capsys):
        """Test bez interfejsów WireGuard."""
        data = {"hostname": "no-wg", "wg_status": {"wg-mgmt": {"service_active": True}}}
        with patch('ai_assistant.ai_chat.run_cmd', return_value="N/A"):
            show_server_context(data)
        captured = capsys.readouterr()
        assert "N/A" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
