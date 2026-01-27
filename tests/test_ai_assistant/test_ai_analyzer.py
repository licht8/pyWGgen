#!/usr/bin/env python3
"""
Testy jednostkowe analizatora AI dla diagnostyki WireGuard VPN.

Moduł testuje integrację z lokalnym AI (Ollama):
- Przygotowywanie promptów diagnostycznych
- Analiza danych systemowych (WireGuard, firewall, NAT, peers)
- Obsługa błędów JSON i timeoutów
- Interaktywne pytania do AI
"""

import pytest
import os
import json
import sys
from unittest.mock import Mock, patch
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ai_assistant.ai_analyzer import (
    prepare_prompt, 
    analyze_with_ai, 
    interactive_question
)


class TestAIAnalyzer:
    """Testy jednostkowe dla AI VPN Analyzer."""

    @pytest.fixture
    def sample_diagnostic_data(self):
        """Przykładowe dane diagnostyczne."""
        return {
            "hostname": "vpn-server-01",
            "wg_status": {
                "wg0": {"service_active": True},
                "wg1": {"service_active": False}
            },
            "firewalld": {
                "active": "aktywny",
                "wg_port_open": True
            },
            "nat": {
                "ok": True,
                "reason": "iptables MASQUERADE active",
                "ip_forward": True
            },
            "peers_active": 5,
            "peers_configured": 10,
            "user_peer_files": {"total": 12},
            "wg_active": 1,
            "wg_total": 2
        }

    def test_prepare_prompt_ok_status(self, sample_diagnostic_data):
        """Test promptu dla stanu OK."""
        prompt = prepare_prompt(sample_diagnostic_data)
        assert "Jesteś ekspertem WireGuard VPN" in prompt
        assert "vpn-server-01" in prompt
        assert "wg0 (aktywny), wg1 (nieaktywny)" in prompt

    def test_prepare_prompt_nat_problem(self):
        """Test promptu gdy NAT ma problem."""
        data = {
            "hostname": "test-server",
            "wg_status": {"wg0": {"service_active": True}},
            "firewalld": {"active": "aktywny", "wg_port_open": True},
            "nat": {"ok": False, "reason": "MASQUERADE missing"},
            "peers_active": 0,
            "peers_configured": 5,
            "user_peer_files": {"total": 5}
        }
        prompt = prepare_prompt(data)
        assert "NAT: PROBLEM" in prompt

    def test_prepare_prompt_missing_keys(self):
        """Test obsługi brakujących kluczy w danych."""
        minimal_data = {"hostname": "minimal"}
        prompt = prepare_prompt(minimal_data)
        assert "Jesteś ekspertem WireGuard VPN" in prompt

    @patch('ai_assistant.ai_analyzer.run_cmd')
    def test_analyze_with_ai_success(self, mock_run_cmd, sample_diagnostic_data):
        """Test analizy AI - sukces."""
        mock_run_cmd.return_value = json.dumps({
            "model": "llama3.2", 
            "response": "🟢 Status: OK | Ocena: 95/100"
        })
        
        result = analyze_with_ai(sample_diagnostic_data)
        assert "Status: OK" in result
        assert "Ocena: 95/100" in result
        mock_run_cmd.assert_called_once()

    @patch('ai_assistant.ai_analyzer.run_cmd')
    def test_analyze_with_ai_json_error(self, mock_run_cmd):
        """Test błędu parsowania JSON."""
        mock_run_cmd.return_value = '{"invalid": "json"} invalid'
        result = analyze_with_ai({})
        assert "Błąd parsowania odpowiedzi" in result

    @patch('ai_assistant.ai_analyzer.run_cmd', return_value="Error: timeout")
    def test_analyze_with_ai_run_error(self, mock_run_cmd):
        """Test błędu polecenia run_cmd."""
        result = analyze_with_ai({})
        assert "Błąd zapytania do AI" in result

    @patch('ai_assistant.ai_analyzer.run_cmd', side_effect=Exception("Connection error"))
    def test_analyze_with_ai_cleanup(self, mock_run_cmd):
        """Test obsługi wyjątków."""
        result = analyze_with_ai({})
        assert "Błąd: Connection error" in result

    @patch('ai_assistant.ai_analyzer.run_cmd')
    def test_interactive_question_success(self, mock_run_cmd):
        """Test interaktywnego pytania - sukces."""
        mock_run_cmd.return_value = json.dumps({
            "response": "Włącz iptables MASQUERADE"
        })
        
        result = interactive_question({}, "Jak naprawić NAT?")
        assert "MASQUERADE" in result

    @patch('ai_assistant.ai_analyzer.run_cmd', return_value="Error")
    def test_interactive_question_error(self, mock_run_cmd):
        """Test błędu interaktywnego pytania."""
        result = interactive_question({}, "test")
        assert "Błąd zapytania" in result

    def test_prepare_prompt_empty_wg_status(self):
        """Test pustego statusu WireGuard."""
        data = {"hostname": "empty", "wg_status": {}}
        prompt = prepare_prompt(data)
        assert "Interfejsy WireGuard:" in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
