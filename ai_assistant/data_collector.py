#!/usr/bin/env python3
"""Сборщик данных для AI диагностики."""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings

from .utils import run_cmd


def parse_wg_config(config_path: Path) -> Dict[str, Any]:
    """Парсинг WireGuard конфига для извлечения peer информации."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        peers = []
        current_peer = {}
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line.startswith('[Peer]'):
                if current_peer:
                    peers.append(current_peer)
                current_peer = {}
            
            elif '=' in line and current_peer is not None:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'PublicKey':
                    current_peer['public_key'] = value
                elif key == 'AllowedIPs':
                    current_peer['allowed_ips'] = value
                elif key == 'PresharedKey':
                    current_peer['has_psk'] = True
                elif key == 'Endpoint':
                    current_peer['endpoint'] = value
        
        # Добавить последний peer
        if current_peer:
            peers.append(current_peer)
        
        return {
            'config_file': str(config_path),
            'peers_count': len(peers),
            'peers': peers
        }
    
    except Exception as e:
        return {'error': str(e), 'config_file': str(config_path)}


def get_all_peer_configs() -> List[Dict[str, Any]]:
    """Получить все peer конфиги из файлов."""
    peer_configs = []
    wg_conf_dir = Path('/etc/wireguard')
    
    if not wg_conf_dir.exists():
        return peer_configs
    
    # Парсинг всех .conf файлов
    for conf_file in wg_conf_dir.glob('*.conf'):
        config_data = parse_wg_config(conf_file)
        if 'peers' in config_data and config_data['peers']:
            peer_configs.append(config_data)
    
    return peer_configs


def get_user_peer_files() -> Dict[str, Any]:
    """Получить информацию о peer файлах пользователей из user/configs/."""
    try:
        # Правильный путь из settings
        user_configs_dir = settings.WG_CONFIG_DIR
        
        if not user_configs_dir.exists():
            return {
                'total': 0,
                'peers': [],
                'error': f'Директория {user_configs_dir} не существует'
            }
        
        peer_files = []
        
        # Поиск всех .conf файлов в user/configs/
        for conf_file in user_configs_dir.rglob('*.conf'):
            try:
                stat = conf_file.stat()
                
                # Попробовать прочитать PublicKey из файла
                public_key = None
                allowed_ips = None
                
                with open(conf_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if 'PublicKey' in line and '=' in line:
                            public_key = line.split('=')[1].strip()
                        if 'AllowedIPs' in line and '=' in line:
                            allowed_ips = line.split('=')[1].strip()
                
                peer_files.append({
                    'filename': conf_file.name,
                    'path': str(conf_file),
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                    'public_key': public_key,
                    'allowed_ips': allowed_ips
                })
            
            except Exception as e:
                peer_files.append({
                    'filename': conf_file.name,
                    'path': str(conf_file),
                    'error': str(e)
                })
        
        return {
            'total': len(peer_files),
            'peers': peer_files,
            'directory': str(user_configs_dir)
        }
    
    except Exception as e:
        return {
            'total': 0,
            'peers': [],
            'error': str(e)
        }


def get_wg_status() -> Dict[str, Any]:
    """Детальный статус WireGuard интерфейсов."""
    result = {}
    
    # Все интерфейсы
    interfaces = run_cmd("wg show interfaces")
    if not interfaces:
        return result
    
    for iface in interfaces.split():
        iface = iface.strip()
        if not iface:
            continue
        
        # Статус сервиса
        service_status = run_cmd(f"systemctl is-active wg-quick@{iface}")
        service_enabled = run_cmd(f"systemctl is-enabled wg-quick@{iface}")
        
        # IP link статус
        link_status = run_cmd(f"ip link show {iface}")
        link_up = "UP" in link_status if link_status else False
        
        # Listening port
        listen_port = run_cmd(f"wg show {iface} listen-port")
        
        # Peers dump (детальная инфа)
        peers_dump = run_cmd(f"wg show {iface} dump")
        
        # Парсинг peers
        peers = []
        if peers_dump:
            lines = peers_dump.strip().split('\n')[1:]  # Пропустить заголовок
            for line in lines:
                parts = line.split('\t')
                if len(parts) >= 8:
                    peers.append({
                        'public_key': parts[0],
                        'preshared_key': parts[1] if parts[1] != '(none)' else None,
                        'endpoint': parts[2] if parts[2] != '(none)' else None,
                        'allowed_ips': parts[3],
                        'latest_handshake': int(parts[4]) if parts[4] != '0' else 0,
                        'rx_bytes': int(parts[5]),
                        'tx_bytes': int(parts[6]),
                        'keepalive': parts[7]
                    })
        
        result[iface] = {
            'service_status': service_status,
            'service_enabled': service_enabled,
            'service_active': service_status == 'active',
            'link_up': link_up,
            'listen_port': listen_port,
            'peers_active': len(peers),
            'peers': peers
        }
    
    return result


def get_firewalld_status() -> Dict[str, Any]:
    """Статус firewalld."""
    active = run_cmd("systemctl is-active firewalld")
    zones = run_cmd("firewall-cmd --get-active-zones")
    
    # Проверка WireGuard порта
    wg_port_open = False
    wg_port = run_cmd("wg show all listen-port")
    
    if wg_port:
        # Проверка в портах
        port_check = run_cmd(f"firewall-cmd --list-ports | grep {wg_port}")
        wg_port_open = bool(port_check)
        
        # Если не нашли, проверяем в rich rules
        if not wg_port_open:
            rich_rules = run_cmd("firewall-cmd --list-rich-rules")
            if rich_rules and wg_port in rich_rules:
                wg_port_open = True
    
    # Список открытых портов
    ports = run_cmd("firewall-cmd --list-ports")
    
    return {
        'active': active,
        'zones': zones,
        'wg_port': wg_port,
        'wg_port_open': wg_port_open,
        'ports': ports
    }


def get_nat_status() -> Dict[str, Any]:
    """Проверка NAT/Masquerade - расширенная."""
    ip_forward = run_cmd("sysctl -n net.ipv4.ip_forward")
    
    # Проверка iptables NAT
    iptables_nat = run_cmd("iptables -t nat -L POSTROUTING -n -v")
    
    # Проверка nftables NAT
    nft_nat = run_cmd("nft list ruleset | grep -i masquerade")
    
    # Проверка firewalld masquerade по зонам
    zones_masq = {}
    zones_output = run_cmd("firewall-cmd --get-active-zones")
    if zones_output:
        for line in zones_output.split('\n'):
            zone = line.strip()
            if zone and not line.startswith(' '):
                masq_check = run_cmd(f"firewall-cmd --zone={zone} --query-masquerade")
                zones_masq[zone] = (masq_check == "yes")
    
    # Проверка rich rules
    rich_rules = run_cmd("firewall-cmd --list-rich-rules")
    rich_masq = "masquerade" in rich_rules.lower() if rich_rules else False
    
    # Детальная проверка NAT
    nat_checks = {
        'ip_forward': ip_forward == "1",
        'iptables_masquerade': "MASQUERADE" in iptables_nat or "SNAT" in iptables_nat,
        'nft_masquerade': bool(nft_nat and "masquerade" in nft_nat.lower()),
        'zone_masquerade': any(zones_masq.values()),
        'rich_rules_masquerade': rich_masq
    }
    
    # Общая оценка NAT - исправлено!
    nat_ok = nat_checks['ip_forward'] and (
        nat_checks['iptables_masquerade'] or 
        nat_checks['nft_masquerade'] or 
        nat_checks['zone_masquerade'] or
        nat_checks['rich_rules_masquerade']  # Добавлена проверка rich rules!
    )
    
    # Причина
    reasons = []
    reasons.append(f"ip_forward={1 if nat_checks['ip_forward'] else 0}")
    
    if nat_checks['zone_masquerade']:
        masq_zones = [z for z, m in zones_masq.items() if m]
        reasons.append(f"zone_masquerade_yes={','.join(masq_zones)}")
    else:
        reasons.append("zone_masquerade=no")
    
    if nat_checks['rich_rules_masquerade']:
        reasons.append("rich_rules_masquerade=yes")
    
    if nat_checks['nft_masquerade']:
        reasons.append("nft_masquerade=yes")
    
    if nat_checks['iptables_masquerade']:
        reasons.append("iptables_masquerade=yes")
    
    nat_reason = "; ".join(reasons) if reasons else "Нет NAT правил"
    
    return {
        'ip_forward': nat_checks['ip_forward'],
        'iptables_nat': iptables_nat[:500],
        'nft_nat': nft_nat[:500] if nft_nat else "Нет nft правил",
        'zones_masquerade': zones_masq,
        'rich_rules': rich_rules[:500] if rich_rules else "Нет rich rules",
        'checks': nat_checks,
        'ok': nat_ok,
        'reason': nat_reason
    }


def collect_all_data() -> Dict[str, Any]:
    """Собрать все данные для диагностики."""
    
    # Базовая информация
    hostname = run_cmd("hostname")
    uptime = run_cmd("uptime -p")
    
    # WireGuard статус
    wg_status = get_wg_status()
    wg_active = sum(1 for iface in wg_status.values() if iface.get('service_active'))
    wg_total = len(wg_status)
    
    # Подсчёт активных peers
    total_active_peers = sum(iface.get('peers_active', 0) for iface in wg_status.values())
    
    # Все peer конфиги из /etc/wireguard/*.conf
    all_peer_configs = get_all_peer_configs()
    total_configured_peers = sum(cfg.get('peers_count', 0) for cfg in all_peer_configs)
    
    # Peer файлы пользователей из user/configs/
    user_peers = get_user_peer_files()
    
    # Конфиги WireGuard
    wg_confs = run_cmd("ls -1 /etc/wireguard/*.conf 2>/dev/null")
    wg_confs_list = wg_confs.split('\n') if wg_confs else []
    
    # Firewall & NAT
    firewalld = get_firewalld_status()
    nat = get_nat_status()
    
    # Ollama health check
    from .utils import check_ollama
    try:
        ollama_ok = check_ollama(settings.OLLAMA_HOST)
    except Exception as e:
        print(f"⚠️  Ollama check failed: {e}")
        ollama_ok = False
    
    return {
        'timestamp': run_cmd("date '+%Y-%m-%d %H:%M:%S'"),
        'hostname': hostname,
        'uptime': uptime,
        'wg_active': wg_active,
        'wg_total': wg_total,
        'wg_status': wg_status,
        'wg_confs': wg_confs_list,
        'firewalld': firewalld,
        'nat': nat,
        'peers_active': total_active_peers,
        'peers_configured': total_configured_peers,
        'peer_configs_detail': all_peer_configs,
        'user_peer_files': user_peers,
        'health': {
            'ollama_ok': ollama_ok
        }
    }
