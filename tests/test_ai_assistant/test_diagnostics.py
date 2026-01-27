#!/usr/bin/env python3
"""
Testy jednostkowe diagnostyki WireGuard VPN.

Moduł testuje główną funkcję diagnostyczną:
- Wyświetlanie podsumowania stanu serwera
- Zbieranie danych systemowych (WG, firewall, NAT)
- Zapis logów JSON dla raportów AI
- Obsługa przypadków gdy Ollama niedostępny
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_assistant.diagnostics import print_summary, main


class TestDiagnostics:
    """Testy jednostkowe modułu diagnostyki."""

    @patch('ai_assistant.diagnostics.print')
    def test_print_summary_full(self, mock_print):
        """Test podsumowania z kompletnymi danymi."""
        data = {
            'hostname': 'vpn-server', 'timestamp': '2026-01-18 15:00:00',
            'wg_active': 1, 'wg_total': 2,
            'wg_status': {'wg0': {'service_active': True}},
            'firewalld': {'active': 'active', 'wg_port_open': True},
            'nat': {'ok': True, 'reason': 'OK'},
            'peers_active': 5, 'peers_configured': 10,
            'user_peer_files': {'total': 8},
            'health': {'ollama_ok': True}
        }
        print_summary(data)
        assert mock_print.call_count > 5

    @patch('ai_assistant.diagnostics.print')
    def test_print_summary_minimal(self, mock_print):
        """Test podsumowania z minimalnymi danymi."""
        data = {
            'hostname': 'test', 'timestamp': '2026-01-18 15:00:00',
            'wg_active': 0, 'wg_total': 0, 'wg_status': {},
            'firewalld': {'active': 'inactive'}, 'nat': {'ok': False},
            'peers_active': 0, 'peers_configured': 0, 'user_peer_files': {'total': 0},
            'health': {'ollama_ok': False}
        }
        print_summary(data)
        assert mock_print.call_count > 3

    @patch('ai_assistant.diagnostics.collect_all_data')
    @patch('ai_assistant.diagnostics.save_json_log')
    @patch('ai_assistant.utils.check_ollama', return_value=False)
    @patch('ai_assistant.diagnostics.print_summary')
    def test_main_flow_structure(self, mock_print_summary, mock_check_ollama, mock_save_log, mock_collect_data):
        """Test struktury głównego przepływu."""
        mock_data = {'hostname': 'vpn-server'}
        mock_collect_data.return_value = mock_data
        mock_save_log.return_value = '/tmp/diag.json'
        
        main()

    @patch('ai_assistant.diagnostics.collect_all_data')
    @patch('ai_assistant.diagnostics.save_json_log')
    @patch('ai_assistant.utils.check_ollama', return_value=False)
    @patch('ai_assistant.diagnostics.print_summary')
    def test_main_ollama_down(self, mock_print_summary, mock_check_ollama, mock_save_log, mock_collect_data):
        """Test gdy Ollama jest niedostępny."""
        mock_data = {'hostname': 'vpn-server'}
        mock_collect_data.return_value = mock_data
        mock_save_log.return_value = '/tmp/diag.json'
        
        main()

    @patch('ai_assistant.diagnostics.collect_all_data')
    @patch('ai_assistant.diagnostics.save_json_log')
    def test_main_minimal(self, mock_save_log, mock_collect_data, capsys):
        """Test minimalny z przechwytywaniem outputu."""
        mock_data = {'hostname': 'test'}
        mock_collect_data.return_value = mock_data
        mock_save_log.return_value = '/tmp/test.json'
        
        main()
        captured = capsys.readouterr()

    def test_print_summary_structure(self):
        """Test bezpiecznej struktury danych."""
        data = {'wg_status': {}, 'firewalld': {}, 'nat': {}, 'health': {}}
        print_summary(data)

    @patch('ai_assistant.diagnostics.collect_all_data')
    @patch('ai_assistant.diagnostics.save_json_log')
    @patch('builtins.print')
    def test_main_isolated(self, mock_print, mock_save_log, mock_collect_data):
        """Test izolowany głównej funkcji."""
        mock_data = {'hostname': 'test'}
        mock_collect_data.return_value = mock_data
        mock_save_log.return_value = '/tmp/test.json'
        
        main()
        assert mock_print.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
