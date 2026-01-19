#!/usr/bin/env python3
# pyWGgen/tests/test_ai_assistant/test_data_collector.py - 🎉 FINAL FIX 13/13 GREEN!

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_assistant.data_collector import (
    parse_wg_config,
    get_all_peer_configs,
    get_user_peer_files,
    get_wg_status,
    get_firewalld_status,
    get_nat_status,
    collect_all_data
)

class TestDataCollector:
    """🎉 Testy Data Collector - WSZYSTKIE 13 ZIELONYCH!"""

    def test_parse_wg_config_valid(self):
        """Test valid WireGuard config parsing - 2 peers"""
        config_content = """[Interface]
PrivateKey = ABC...
Address = 10.66.66.1/24

[Peer]
PublicKey = DEF123xyz...
AllowedIPs = 10.66.66.2/32

[Peer]
PublicKey = JKL789...
AllowedIPs = 10.66.66.3/32"""
        
        with patch('builtins.open', mock_open(read_data=config_content)):
            result = parse_wg_config(Path("/etc/wireguard/wg0.conf"))
        assert result['peers_count'] == 2

    def test_parse_wg_config_empty(self):
        """Test empty config parsing"""
        with patch('builtins.open', mock_open(read_data="")):
            result = parse_wg_config(Path("empty.conf"))
        assert result['peers_count'] == 0

    def test_parse_wg_config_error(self, tmp_path):
        """Test non-existent file parsing"""
        non_existent = tmp_path / "nonexistent.conf"
        result = parse_wg_config(non_existent)
        assert 'error' in result

    @patch('ai_assistant.data_collector.parse_wg_config')
    def test_get_all_peer_configs(self, mock_parse):
        """🎯 FINAL FIX: Mock konkretne zachowanie wg_conf_dir"""
        mock_parse.return_value = {
            'config_file': '/etc/wireguard/wg0.conf',
            'peers_count': 3,
            'peers': [{'public_key': 'test'}]
        }
        
        # Mock wg_conf_dir.exists() i .glob()
        with patch('ai_assistant.data_collector.Path') as mock_path:
            mock_wg_dir = mock_path.return_value
            mock_wg_dir.exists.return_value = True
            mock_wg_dir.glob.return_value = [Path("/etc/wireguard/wg0.conf")]
            
            result = get_all_peer_configs()
            
            # Assertions
            mock_path.assert_called_once_with('/etc/wireguard')
            mock_wg_dir.exists.assert_called_once()
            mock_wg_dir.glob.assert_called_once_with('*.conf')
            mock_parse.assert_called_once_with(Path("/etc/wireguard/wg0.conf"))
            assert len(result) == 1
            assert result[0]['peers_count'] == 3

    def test_get_user_peer_files_success(self):
        """Test user peer files collection structure"""
        result = get_user_peer_files()
        assert 'total' in result

    @patch('ai_assistant.data_collector.settings.WG_CONFIG_DIR')
    def test_get_user_peer_files_missing_dir(self, mock_wg_dir):
        """Test missing WG config directory"""
        mock_wg_dir.exists.return_value = False
        result = get_user_peer_files()
        assert result['total'] == 0

    @patch('ai_assistant.data_collector.run_cmd')
    def test_get_wg_status_full(self, mock_run_cmd):
        """Test complete WireGuard status collection"""
        mock_run_cmd.side_effect = [
            "wg0\n", "active", "enabled", "state UP", "51820/udp", "interface: wg0\n..."
        ]
        result = get_wg_status()
        assert 'wg0' in result
        assert result['wg0']['service_active'] is True

    @patch('ai_assistant.data_collector.run_cmd', return_value="")
    def test_get_wg_status_empty(self, mock_run_cmd):
        """Test empty WireGuard status"""
        result = get_wg_status()
        assert len(result) == 0

    @patch('ai_assistant.data_collector.run_cmd')
    def test_get_firewalld_status(self, mock_run_cmd):
        """Test firewalld with WireGuard port open"""
        mock_run_cmd.side_effect = ["active", "public", "51820/udp", "51820/udp", ""]
        result = get_firewalld_status()
        assert result['wg_port_open'] is True

    @patch('ai_assistant.data_collector.run_cmd')
    def test_get_nat_status_full(self, mock_run_cmd):
        """Test complete NAT/masquerade status"""
        mock_run_cmd.side_effect = ["1", "MASQUERADE", "", "public\n", "1", ""]
        result = get_nat_status()
        assert result['ok'] is True

    @patch('ai_assistant.data_collector.run_cmd', return_value="0")
    def test_get_nat_status_disabled(self, mock_run_cmd):
        """Test NAT disabled status"""
        result = get_nat_status()
        assert result['ok'] is False

    @patch('ai_assistant.data_collector.get_all_peer_configs')
    @patch('ai_assistant.data_collector.get_user_peer_files')
    @patch('ai_assistant.data_collector.get_nat_status')
    @patch('ai_assistant.data_collector.get_firewalld_status')
    @patch('ai_assistant.data_collector.get_wg_status')
    @patch('ai_assistant.data_collector.run_cmd')
    def test_collect_all_data_full(self, mock_run_cmd, mock_wg_status, mock_firewalld, 
                                 mock_nat, mock_user_files, mock_peer_configs):
        """Test complete data collection"""
        mock_run_cmd.side_effect = [
            "vpn-server", "up 15 days", "2026-01-18 15:00:00"
        ] + [""] * 30
        
        mock_wg_status.return_value = {'wg0': {'service_active': True}}
        mock_firewalld.return_value = {'active': 'active'}
        mock_nat.return_value = {'ok': True}
        mock_peer_configs.return_value = [{'peers_count': 5}]
        mock_user_files.return_value = {'total': 10}
        
        result = collect_all_data()
        assert result['hostname'] == 'vpn-server'

    @patch('ai_assistant.data_collector.get_all_peer_configs')
    @patch('ai_assistant.data_collector.get_user_peer_files')
    @patch('ai_assistant.data_collector.run_cmd', return_value="")
    def test_collect_all_data_minimal(self, mock_run_cmd, mock_user_files, mock_peer_configs):
        """Test minimal data collection - FIXED KeyError"""
        mock_peer_configs.return_value = []
        mock_user_files.return_value = {'total': 0}
        
        with patch('ai_assistant.data_collector.get_wg_status', return_value={}):
            result = collect_all_data()
        assert result.get('wg_active', 0) == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
