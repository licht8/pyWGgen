#!/usr/bin/env python3
"""AI Report Generator - HTML отчёты с анализом."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings

from .utils import run_cmd


def get_report_dir() -> Path:
    """Получить директорию для отчётов."""
    report_dir = Path(settings.AI_ASSISTANT_LOG_DIR) / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir


def get_previous_logs(limit: int = 5) -> List[Dict[str, Any]]:
    """Получить предыдущие логи диагностики."""
    log_dir = Path(settings.AI_ASSISTANT_LOG_DIR)
    logs = []
    
    for log_file in sorted(log_dir.glob("diag_*.json"), reverse=True)[:limit]:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['_filename'] = log_file.name
                logs.append(data)
        except Exception:
            continue
    
    return logs

def compare_diagnostics(current: Dict[str, Any], previous: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Сравнение текущего состояния с предыдущими."""
    if not previous:
        return {"changes": [], "message": "Нет предыдущих диагностик для сравнения"}
    
    prev = previous[0]
    changes = []
    
    # Сравнение WireGuard
    if current.get("wg_active") != prev.get("wg_active"):
        changes.append(f"WireGuard активных: {prev.get('wg_active')} → {current.get('wg_active')}")
    
    # Сравнение активных peers
    if current.get("peers_active") != prev.get("peers_active"):
        changes.append(f"Активных peers: {prev.get('peers_active', 0)} → {current.get('peers_active', 0)}")
    
    # Сравнение настроенных peers
    if current.get("peers_configured") != prev.get("peers_configured"):
        changes.append(f"Настроенных peers: {prev.get('peers_configured', 0)} → {current.get('peers_configured', 0)}")
    
    # Сравнение пользовательских конфигов
    curr_user_peers = current.get("user_peer_files", {}).get("total", 0)
    prev_user_peers = prev.get("user_peer_files", {}).get("total", 0)
    if curr_user_peers != prev_user_peers:
        changes.append(f"Пользовательских конфигов: {prev_user_peers} → {curr_user_peers}")
    
    # Сравнение NAT
    if current.get("nat", {}).get("ok") != prev.get("nat", {}).get("ok"):
        nat_old = "✅" if prev.get("nat", {}).get("ok") else "❌"
        nat_new = "✅" if current.get("nat", {}).get("ok") else "❌"
        changes.append(f"NAT статус: {nat_old} → {nat_new}")
    
    # Сравнение Firewall
    if current.get("firewalld", {}).get("active") != prev.get("firewalld", {}).get("active"):
        changes.append(f"Firewalld: {prev.get('firewalld', {}).get('active')} → {current.get('firewalld', {}).get('active')}")
    
    return {
        "changes": changes,
        "previous_date": prev.get("timestamp", "unknown"),
        "total_changes": len(changes)
    }


def generate_html_report(data: Dict[str, Any], comparison: Dict[str, Any]) -> str:
    """Генерация HTML отчёта."""
    
    nat = data.get("nat", {})
    fw = data.get("firewalld", {})
    wg_status = data.get("wg_status", {})
    user_peers = data.get('user_peer_files', {})
    
    # Статус иконки
    nat_icon = "🟢" if nat.get("ok") else "🔴"
    fw_icon = "🟢" if fw.get("active") in ["running", "active"] else "🔴"
    ollama_icon = "🟢" if data.get("health", {}).get("ollama_ok") else "🔴"
    
    # Изменения
    changes_html = ""
    if comparison.get("changes"):
        changes_html = "<h2>📊 Изменения с предыдущей диагностики</h2><ul>"
        for change in comparison["changes"]:
            changes_html += f"<li>{change}</li>"
        changes_html += f"</ul><p><em>Предыдущая диагностика: {comparison.get('previous_date')}</em></p>"
    else:
        changes_html = "<p><em>Нет изменений или первая диагностика</em></p>"
    
    # WireGuard интерфейсы
    wg_html = ""
    for iface, info in wg_status.items():
        status = "🟢 Активен" if info.get("service_active") and info.get("link_up") else "🔴 Неактивен"
        peers_count = info.get('peers_active', 0)
        wg_html += f"<li><strong>{iface}</strong>: {status} | Активных peers: {peers_count} | Порт: {info.get('listen_port', 'N/A')}</li>"
    
    # User Peers секция
    user_peers_html = ""
    
    if user_peers.get('peers'):
        user_peers_html = "<h2>👤 Пользовательские конфиги</h2>"
        user_peers_html += f"<p>Всего файлов: <strong>{user_peers.get('total', 0)}</strong> в <code>{user_peers.get('directory')}</code></p>"
        user_peers_html += "<table><tr><th>Файл</th><th>PublicKey</th><th>AllowedIPs</th><th>Размер</th></tr>"
        
        for peer in user_peers['peers']:
            if peer.get('error'):
                user_peers_html += f"""
                <tr>
                    <td><code>{peer.get('filename')}</code></td>
                    <td colspan="3">❌ Ошибка: {peer.get('error')}</td>
                </tr>
                """
            else:
                pk_short = peer.get('public_key', 'N/A')[:20] + '...' if peer.get('public_key') else 'N/A'
                user_peers_html += f"""
                <tr>
                    <td><code>{peer.get('filename')}</code></td>
                    <td><code>{pk_short}</code></td>
                    <td>{peer.get('allowed_ips', 'N/A')}</td>
                    <td>{peer.get('size', 0)} байт</td>
                </tr>
                """
        
        user_peers_html += "</table>"
    else:
        error_msg = user_peers.get('error', 'Конфиги не найдены')
        user_peers_html = f"<h2>👤 Пользовательские конфиги</h2><p>❌ {error_msg}</p>"
    
    # Детали активных peers
    active_peers_html = ""
    for iface, info in wg_status.items():
        peers = info.get('peers', [])
        if peers:
            active_peers_html += f"<h3>Интерфейс: {iface}</h3>"
            active_peers_html += "<table><tr><th>PublicKey</th><th>Endpoint</th><th>AllowedIPs</th><th>Handshake</th><th>RX/TX</th></tr>"
            
            for peer in peers:
                pk_short = peer.get('public_key', '')[:20] + '...'
                endpoint = peer.get('endpoint') or 'N/A'
                allowed = peer.get('allowed_ips', 'N/A')
                handshake = peer.get('latest_handshake', 0)
                
                # Форматирование времени handshake
                if handshake > 0:
                    from datetime import datetime, timedelta
                    hs_time = datetime.now() - timedelta(seconds=handshake)
                    handshake_str = f"{handshake}s назад"
                else:
                    handshake_str = "Нет"
                
                # Форматирование трафика
                rx_mb = peer.get('rx_bytes', 0) / (1024 * 1024)
                tx_mb = peer.get('tx_bytes', 0) / (1024 * 1024)
                traffic = f"↓{rx_mb:.2f} MB / ↑{tx_mb:.2f} MB"
                
                active_peers_html += f"""
                <tr>
                    <td><code>{pk_short}</code></td>
                    <td>{endpoint}</td>
                    <td>{allowed}</td>
                    <td>{handshake_str}</td>
                    <td>{traffic}</td>
                </tr>
                """
            
            active_peers_html += "</table>"
    
    if not active_peers_html:
        active_peers_html = "<p>Нет активных подключений</p>"
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VPN AI Diagnostics Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 5px;
        }}
        h3 {{
            color: #555;
            margin-top: 20px;
        }}
        .status-box {{
            display: inline-block;
            padding: 10px 20px;
            margin: 10px 5px;
            border-radius: 5px;
            background: #ecf0f1;
            font-weight: bold;
        }}
        .status-ok {{
            background: #d4edda;
            color: #155724;
        }}
        .status-error {{
            background: #f8d7da;
            color: #721c24;
        }}
        ul {{
            line-height: 1.8;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #777;
            font-size: 0.9em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #3498db;
            color: white;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
            font-size: 0.9em;
        }}
        .print-btn {{
            background: #3498db;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 20px 0;
        }}
        .print-btn:hover {{
            background: #2980b9;
        }}
        @media print {{
            .print-btn {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <button class="print-btn" onclick="window.print()">🖨️ Печать / Сохранить как PDF</button>
        
        <h1>🚀 VPN AI Diagnostics Report</h1>
        
        <p><strong>Сервер:</strong> {data.get('hostname')}<br>
        <strong>Дата:</strong> {data.get('timestamp')}<br>
        <strong>Uptime:</strong> {data.get('uptime')}</p>
        
        <h2>📡 Общий статус</h2>
        <div class="status-box {'status-ok' if data.get('wg_active') > 0 else 'status-error'}">
            WireGuard: {data.get('wg_active')}/{data.get('wg_total')} активны
        </div>
        <div class="status-box {'status-ok' if nat.get('ok') else 'status-error'}">
            {nat_icon} NAT: {'OK' if nat.get('ok') else 'Проблема'}
        </div>
        <div class="status-box {'status-ok' if fw.get('active') == 'running' else 'status-error'}">
            {fw_icon} Firewalld: {fw.get('active')}
        </div>
        <div class="status-box {'status-ok' if data.get('health', {}).get('ollama_ok') else 'status-error'}">
            {ollama_icon} Ollama AI: {'Доступен' if data.get('health', {}).get('ollama_ok') else 'Недоступен'}
        </div>
        
        {changes_html}
        
        <h2>🔧 WireGuard интерфейсы</h2>
        <ul>{wg_html if wg_html else '<li>Нет активных интерфейсов</li>'}</ul>
        
        <h2>👥 Статистика Peers</h2>
        <table>
            <tr>
                <th>Параметр</th>
                <th>Значение</th>
            </tr>
            <tr>
                <td>Активных peers (подключены сейчас)</td>
                <td><strong>{data.get('peers_active', 0)}</strong></td>
            </tr>
            <tr>
                <td>Настроено peers (в /etc/wireguard/*.conf)</td>
                <td><strong>{data.get('peers_configured', 0)}</strong></td>
            </tr>
            <tr>
                <td>Пользовательских конфигов (user/configs/)</td>
                <td><strong>{user_peers.get('total', 0)}</strong></td>
            </tr>
        </table>
        
        <h2>🔗 Активные подключения</h2>
        {active_peers_html}
        
        {user_peers_html}
        
        <h2>🔥 Firewall & NAT</h2>
        <table>
            <tr>
                <th>Параметр</th>
                <th>Значение</th>
            </tr>
            <tr>
                <td>Firewalld статус</td>
                <td>{fw.get('active')}</td>
            </tr>
            <tr>
                <td>WG порт открыт</td>
                <td>{'✅ Да' if fw.get('wg_port_open') else '❌ Нет'} (порт: {fw.get('wg_port', 'N/A')})</td>
            </tr>
            <tr>
                <td>IP Forwarding</td>
                <td>{'✅ Включён' if nat.get('ip_forward') else '❌ Выключен'}</td>
            </tr>
            <tr>
                <td>NAT Masquerade</td>
                <td>{'✅ Настроен' if nat.get('ok') else '❌ Не настроен'}</td>
            </tr>
            <tr>
                <td>NAT детали</td>
                <td><code>{nat.get('reason', '')}</code></td>
            </tr>
        </table>
        
        <h2>📊 Конфигурационные файлы</h2>
        <p>Всего конфигов WireGuard: <strong>{len(data.get('wg_confs', []))}</strong></p>
        <ul>
            {''.join([f"<li><code>{conf}</code></li>" for conf in data.get('wg_confs', [])])}
        </ul>
        
        <div class="footer">
            <p>Отчёт сгенерирован AI Assistant VPN | pyWGgen v2.4</p>
            <p>Полные данные диагностики сохранены в JSON логе</p>
        </div>
    </div>
    
    <script>
        // Автоматически открыть диалог печати (опционально)
        // window.onload = function() {{ window.print(); }}
    </script>
</body>
</html>"""
    
    return html


def generate_report(data: Dict[str, Any]) -> str:
    """Главная функция генерации отчёта."""
    report_dir = get_report_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Получить предыдущие диагностики
    previous_logs = get_previous_logs(limit=5)
    comparison = compare_diagnostics(data, previous_logs)
    
    # Генерация HTML
    html_content = generate_html_report(data, comparison)
    html_path = report_dir / f"report_{ts}.html"
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return str(html_path)


def show_report_menu(data: Dict[str, Any]):
    """Интерактивное меню генерации отчёта."""
    print("\n📄 AI REPORT GENERATOR")
    print("=" * 72)
    print("Генерация HTML отчёта...")
    
    html_path = generate_report(data)
    
    print("\n✅ Отчёт сгенерирован!")
    print("=" * 72)
    print(f"📄 HTML: {html_path}")
    print(f"\n💡 Открой в браузере:")
    print(f"   file://{html_path}")
    print(f"\n🖨️  Для сохранения в PDF:")
    print(f"   Открой HTML → Ctrl+P → Сохранить как PDF")
    print(f"\n💾 Все отчёты: {get_report_dir()}")
