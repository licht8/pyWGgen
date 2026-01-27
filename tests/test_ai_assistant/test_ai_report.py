#!/usr/bin/env python3
"""
Testy jednostkowe generatora raportów AI dla diagnostyki WireGuard VPN.

Moduł testuje generowanie raportów HTML:
- Automatyczne katalogi raportów (raporty/)
- Porównywanie diagnostyk między pomiarami
- Generowanie HTML z tabelami i emoji statusów
- Menu interaktywne raportów
- Obsługa brakujących danych i uprawnień
"""

import pytest
import os
import json
import sys
from unittest.mock import Mock, patch
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ai_assistant.ai_report import (
    get_report_dir,
    get_previous_logs,
    compare_diagnostics,
    generate_html_report,
    generate_report,
    show_report_menu
)


class TestAIReport:
    """Testy jednostkowe dla AI Report Generator."""

    @pytest.fixture
    def sample_diagnostic_data(self):
        """Przykładowe dane diagnostyczne."""
        return {
            "hostname": "vpn-server-01",
            "timestamp": "2026-01-18 14:30:00",
            "uptime": "15 days",
            "wg_active": 1,
            "wg_total": 2,
            "peers_active": 5,
            "peers_configured": 25,
            "user_peer_files": {"total": 28, "directory": "/etc/wireguard/user_configs"},
            "firewalld": {"active": "aktywny", "wg_port": "51820", "wg_port_open": True},
            "nat": {"ok": True, "reason": "MASQUERADE active", "ip_forward": True},
            "health": {"ollama_ok": True},
            "wg_status": {
                "wg0": {
                    "service_active": True,
                    "link_up": True,
                    "listen_port": "51820",
                    "peers_active": 5,
                    "peers": [{"public_key": "ABC...", "latest_handshake": 300}]
                }
            },
            "wg_confs": ["/etc/wireguard/wg0.conf"]
        }

    @pytest.fixture
    def sample_previous_data(self):
        """Poprzednie dane diagnostyczne."""
        return {
            "wg_active": 0,
            "peers_active": 2,
            "peers_configured": 20,
            "user_peer_files": {"total": 25},
            "nat": {"ok": False},
            "firewalld": {"active": "nieaktywny"},
            "timestamp": "2026-01-17 12:00:00"
        }

    def test_get_report_dir(self, tmp_path):
        """Test katalogu raportów."""
        with patch('ai_assistant.ai_report.settings.AI_ASSISTANT_LOG_DIR', str(tmp_path)):
            report_dir = get_report_dir()
            assert report_dir.exists()
            assert str(report_dir).endswith("raporty")

    def test_get_previous_logs_empty(self, tmp_path):
        """Test brak poprzednich logów."""
        with patch('ai_assistant.ai_report.settings.AI_ASSISTANT_LOG_DIR', str(tmp_path)):
            with patch('pathlib.Path.glob', return_value=[]):
                logs = get_previous_logs()
            assert logs == []

    def test_compare_diagnostics_no_previous(self):
        """Test brak poprzednich diagnostyk."""
        comparison = compare_diagnostics({}, [])
        assert comparison["zmiany"] == []
        assert "Brak poprzednich" in comparison["wiadomosc"]

    def test_compare_diagnostics_changes(self, sample_diagnostic_data, sample_previous_data):
        """Test wykrywanie zmian diagnostycznych."""
        comparison = compare_diagnostics(sample_diagnostic_data, [sample_previous_data])
        assert len(comparison["zmiany"]) >= 2
        assert comparison["data_poprzednia"] == "2026-01-17 12:00:00"

    def test_compare_diagnostics_no_changes(self, sample_diagnostic_data):
        """Test brak zmian diagnostycznych."""
        comparison = compare_diagnostics(sample_diagnostic_data, [sample_diagnostic_data])
        assert comparison["zmiany"] == []
        assert comparison["laczna_liczba_zmian"] == 0

    def test_compare_diagnostics_missing_keys(self):
        """Test obsługi brakujących kluczy."""
        current = {"wg_active": 1}
        previous = [{"wg_active": 0}]
        comparison = compare_diagnostics(current, previous)
        assert len(comparison["zmiany"]) == 1
        assert "WireGuard aktywnych: 0 → 1" in comparison["zmiany"][0]

    def test_generate_html_report_structure(self, sample_diagnostic_data):
        """Test struktury raportu HTML."""
        comparison = {"zmiany": []}
        html = generate_html_report(sample_diagnostic_data, comparison)
        
        assert "<!DOCTYPE html>" in html
        assert "Raport diagnostyki VPN AI" in html
        assert "vpn-server-01" in html
        assert "1/2 aktywnych" in html
        assert "🟢" in html

    def test_generate_html_report_user_peers(self, sample_diagnostic_data):
        """Test sekcji peers w raporcie HTML."""
        sample_diagnostic_data["user_peer_files"]["peers"] = [
            {"filename": "user1.conf", "public_key": "ABC123...", "allowed_ips": "10.66.66.2/32", "size": 123}
        ]
        comparison = {"zmiany": []}
        html = generate_html_report(sample_diagnostic_data, comparison)
        assert "user1.conf" in html
        assert "<table>" in html

    def test_generate_html_report_no_active_peers(self, sample_diagnostic_data):
        """Test brak aktywnych peers w raporcie."""
        sample_diagnostic_data["wg_status"]["wg0"]["peers"] = []
        comparison = {"zmiany": []}
        html = generate_html_report(sample_diagnostic_data, comparison)
        assert "Brak aktywnych połączeń" in html

    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists', return_value=False)
    @patch('builtins.open')
    def test_generate_report_full_flow(self, mock_open, mock_exists, mock_mkdir, tmp_path):
        """Test pełnego przepływu generowania raportu."""
        with patch('ai_assistant.ai_report.settings.AI_ASSISTANT_LOG_DIR', str(tmp_path)):
            with patch('ai_assistant.ai_report.get_previous_logs', return_value=[]):
                data = {"hostname": "test", "wg_total": 1, "wg_active": 1}
                html_path = generate_report(data)
                
                assert "raport_" in html_path
                assert html_path.endswith(".html")
                assert "raporty" in html_path
                mock_open.assert_called()

    @patch('builtins.print')
    def test_show_report_menu(self, mock_print, sample_diagnostic_data):
        """Test menu raportów."""
        with patch('ai_assistant.ai_report.generate_report', return_value="/tmp/raport.html"):
            show_report_menu(sample_diagnostic_data)
        
        output = mock_print.call_args_list
        assert any("GENERATOR RAPORTÓW AI" in str(call) for call in output)

    def test_get_report_dir_permissions(self, tmp_path):
        """Test uprawnienia katalogu raportów."""
        with patch('ai_assistant.ai_report.settings.AI_ASSISTANT_LOG_DIR', str(tmp_path)):
            report_dir = get_report_dir()
            assert report_dir.is_dir()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
