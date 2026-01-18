#!/usr/bin/env python3
"""Generator raportów AI - raporty HTML z analizą."""

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
    """Pobiera katalog dla raportów."""
    report_dir = Path(settings.AI_ASSISTANT_LOG_DIR) / "raporty"
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir


def get_previous_logs(limit: int = 5) -> List[Dict[str, Any]]:
    """Pobiera poprzednie logi diagnostyczne."""
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
    """Porównuje aktualny stan z poprzednimi."""
    if not previous:
        return {"zmiany": [], "wiadomosc": "Brak poprzednich diagnostyk do porównania"}
    
    prev = previous[0]
    changes = []
    
    # Porównanie WireGuard
    if current.get("wg_active") != prev.get("wg_active"):
        changes.append(f"WireGuard aktywnych: {prev.get('wg_active')} → {current.get('wg_active')}")
    
    # Porównanie aktywnych peers
    if current.get("peers_active") != prev.get("peers_active"):
        changes.append(f"Aktywnych peers: {prev.get('peers_active', 0)} → {current.get('peers_active', 0)}")
    
    # Porównanie skonfigurowanych peers
    if current.get("peers_configured") != prev.get("peers_configured"):
        changes.append(f"Skonfigurowanych peers: {prev.get('peers_configured', 0)} → {current.get('peers_configured', 0)}")
    
    # Porównanie konfiguracji użytkowników
    curr_user_peers = current.get("user_peer_files", {}).get("total", 0)
    prev_user_peers = prev.get("user_peer_files", {}).get("total", 0)
    if curr_user_peers != prev_user_peers:
        changes.append(f"Konfiguracji użytkowników: {prev_user_peers} → {curr_user_peers}")
    
    # Porównanie NAT
    if current.get("nat", {}).get("ok") != prev.get("nat", {}).get("ok"):
        nat_old = "✅" if prev.get("nat", {}).get("ok") else "❌"
        nat_new = "✅" if current.get("nat", {}).get("ok") else "❌"
        changes.append(f"Status NAT: {nat_old} → {nat_new}")
    
    # Porównanie Firewall
    if current.get("firewalld", {}).get("active") != prev.get("firewalld", {}).get("active"):
        changes.append(f"Firewalld: {prev.get('firewalld', {}).get('active')} → {current.get('firewalld', {}).get('active')}")
    
    return {
        "zmiany": changes,
        "data_poprzednia": prev.get("timestamp", "nieznana"),
        "laczna_liczba_zmian": len(changes)
    }


def generate_html_report(data: Dict[str, Any], comparison: Dict[str, Any]) -> str:
    """Generuje raport HTML."""
    
    nat = data.get("nat", {})
    fw = data.get("firewalld", {})
    wg_status = data.get("wg_status", {})
    user_peers = data.get('user_peer_files', {})
    
    # Ikonki statusu
    nat_icon = "🟢" if nat.get("ok") else "🔴"
    fw_icon = "🟢" if fw.get("active") in ["running", "active"] else "🔴"
    ollama_icon = "🟢" if data.get("health", {}).get("ollama_ok") else "🔴"
    
    # Zmiany
    changes_html = ""
    if comparison.get("zmiany"):
        changes_html = "<h2>📊 Zmiany od poprzedniej diagnostyki</h2><ul>"
        for change in comparison["zmiany"]:
            changes_html += f"<li>{change}</li>"
        changes_html += f"</ul><p><em>Poprzednia diagnostyka: {comparison.get('data_poprzednia')}</em></p>"
    else:
        changes_html = "<p><em>Brak zmian lub pierwsza diagnostyka</em></p>"
    
    # Interfejsy WireGuard
    wg_html = ""
    for iface, info in wg_status.items():
        status = "🟢 Aktywny" if info.get("service_active") and info.get("link_up") else "🔴 Nieaktywny"
        peers_count = info.get('peers_active', 0)
        wg_html += f"<li><strong>{iface}</strong>: {status} | Aktywnych peers: {peers_count} | Port: {info.get('listen_port', 'N/A')}</li>"
    
    # Sekcja User Peers
    user_peers_html = ""
    
    if user_peers.get('peers'):
        user_peers_html = "<h2>👤 Konfiguracje użytkowników</h2>"
        user_peers_html += f"<p>Łącznie plików: <strong>{user_peers.get('total', 0)}</strong> w <code>{user_peers.get('directory')}</code></p>"
        user_peers_html += "<table><tr><th>Plik</th><th>PublicKey</th><th>AllowedIPs</th><th>Rozmiar</th></tr>"
        
        for peer in user_peers['peers']:
            if peer.get('error'):
                user_peers_html += f"""
                <tr>
                    <td><code>{peer.get('filename')}</code></td>
                    <td colspan="3">❌ Błąd: {peer.get('error')}</td>
                </tr>
                """
            else:
                pk_short = peer.get('public_key', 'N/A')[:20] + '...' if peer.get('public_key') else 'N/A'
                user_peers_html += f"""
                <tr>
                    <td><code>{peer.get('filename')}</code></td>
                    <td><code>{pk_short}</code></td>
                    <td>{peer.get('allowed_ips', 'N/A')}</td>
                    <td>{peer.get('size', 0)} bajtów</td>
                </tr>
                """
        
        user_peers_html += "</table>"
    else:
        error_msg = user_peers.get('error', 'Nie znaleziono konfiguracji')
        user_peers_html = f"<h2>👤 Konfiguracje użytkowników</h2><p>❌ {error_msg}</p>"
    
    # Szczegóły aktywnych peers
    active_peers_html = ""
    for iface, info in wg_status.items():
        peers = info.get('peers', [])
        if peers:
            active_peers_html += f"<h3>Interfejs: {iface}</h3>"
            active_peers_html += "<table><tr><th>PublicKey</th><th>Endpoint</th><th>AllowedIPs</th><th>Handshake</th><th>RX/TX</th></tr>"
            
            for peer in peers:
                pk_short = peer.get('public_key', '')[:20] + '...'
                endpoint = peer.get('endpoint') or 'N/A'
                allowed = peer.get('allowed_ips', 'N/A')
                handshake = peer.get('latest_handshake', 0)
                
                # Formatowanie czasu handshake
                if handshake > 0:
                    from datetime import datetime, timedelta
                    hs_time = datetime.now() - timedelta(seconds=handshake)
                    handshake_str = f"{handshake}s temu"
                else:
                    handshake_str = "Brak"
                
                # Formatowanie ruchu
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
        active_peers_html = "<p>Brak aktywnych połączeń</p>"
    
    html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Raport diagnostyki VPN AI</title>
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
        <button class="print-btn" onclick="window.print()">🖨️ Drukuj / Zapisz jako PDF</button>
        
        <h1>🚀 Raport diagnostyki VPN AI</h1>
        
        <p><strong>Serwer:</strong> {data.get('hostname')}<br>
        <strong>Data:</strong> {data.get('timestamp')}<br>
        <strong>Czas pracy:</strong> {data.get('uptime')}</p>
        
        <h2>📡 Ogólny status</h2>
        <div class="status-box {'status-ok' if data.get('wg_active') > 0 else 'status-error'}">
            WireGuard: {data.get('wg_active')}/{data.get('wg_total')} aktywnych
        </div>
        <div class="status-box {'status-ok' if nat.get('ok') else 'status-error'}">
            {nat_icon} NAT: {'OK' if nat.get('ok') else 'Problem'}
        </div>
        <div class="status-box {'status-ok' if fw.get('active') == 'running' else 'status-error'}">
            {fw_icon} Firewalld: {fw.get('active')}
        </div>
        <div class="status-box {'status-ok' if data.get('health', {}).get('ollama_ok') else 'status-error'}">
            {ollama_icon} Ollama AI: {'Dostępny' if data.get('health', {}).get('ollama_ok') else 'Niedostępny'}
        </div>
        
        {changes_html}
        
        <h2>🔧 Interfejsy WireGuard</h2>
        <ul>{wg_html if wg_html else '<li>Brak aktywnych interfejsów</li>'}</ul>
        
        <h2>👥 Statystyka Peers</h2>
        <table>
            <tr>
                <th>Parametr</th>
                <th>Wartość</th>
            </tr>
            <tr>
                <td>Aktywnych peers (połączonych teraz)</td>
                <td><strong>{data.get('peers_active', 0)}</strong></td>
            </tr>
            <tr>
                <td>Skonfigurowanych peers (w /etc/wireguard/*.conf)</td>
                <td><strong>{data.get('peers_configured', 0)}</strong></td>
            </tr>
            <tr>
                <td>Konfiguracji użytkowników (user/configs/)</td>
                <td><strong>{user_peers.get('total', 0)}</strong></td>
            </tr>
        </table>
        
        <h2>🔗 Aktywne połączenia</h2>
        {active_peers_html}
        
        {user_peers_html}
        
        <h2>🔥 Firewall & NAT</h2>
        <table>
            <tr>
                <th>Parametr</th>
                <th>Wartość</th>
            </tr>
            <tr>
                <td>Status Firewalld</td>
                <td>{fw.get('active')}</td>
            </tr>
            <tr>
                <td>Port WG otwarty</td>
                <td>{'✅ Tak' if fw.get('wg_port_open') else '❌ Nie'} (port: {fw.get('wg_port', 'N/A')})</td>
            </tr>
            <tr>
                <td>IP Forwarding</td>
                <td>{'✅ Włączony' if nat.get('ip_forward') else '❌ Wyłączony'}</td>
            </tr>
            <tr>
                <td>NAT Masquerade</td>
                <td>{'✅ Skonfigurowany' if nat.get('ok') else '❌ Nieskonfigurowany'}</td>
            </tr>
            <tr>
                <td>Szczegóły NAT</td>
                <td><code>{nat.get('reason', '')}</code></td>
            </tr>
        </table>
        
        <h2>📊 Pliki konfiguracyjne</h2>
        <p>Łącznie konfiguracji WireGuard: <strong>{len(data.get('wg_confs', []))}</strong></p>
        <ul>
            {''.join([f"<li><code>{conf}</code></li>" for conf in data.get('wg_confs', [])])}
        </ul>
        
        <div class="footer">
            <p>Raport wygenerowany przez Asystenta AI VPN | pyWGgen v2.4</p>
            <p>Pełne dane diagnostyczne zapisane w logu JSON</p>
        </div>
    </div>
    
    <script>
        // Automatycznie otworzyć okno drukowania (opcjonalnie)
        // window.onload = function() {{ window.print(); }}
    </script>
</body>
</html>"""
    
    return html


def generate_report(data: Dict[str, Any]) -> str:
    """Główna funkcja generowania raportu."""
    report_dir = get_report_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Pobierz poprzednie diagnostyki
    previous_logs = get_previous_logs(limit=5)
    comparison = compare_diagnostics(data, previous_logs)
    
    # Generowanie HTML
    html_content = generate_html_report(data, comparison)
    html_path = report_dir / f"raport_{ts}.html"
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return str(html_path)


def show_report_menu(data: Dict[str, Any]):
    """Interaktywne menu generowania raportu."""
    print("\n📄 GENERATOR RAPORTÓW AI")
    print("=" * 72)
    print("Generowanie raportu HTML...")
    
    html_path = generate_report(data)
    
    print("\n✅ Raport wygenerowany!")
    print("=" * 72)
    print(f"📄 HTML: {html_path}")
    print(f"\n💡 Otwórz w przeglądarce:")
    print(f"   file://{html_path}")
    print(f"\n🖨️  Aby zapisać jako PDF:")
    print(f"   Otwórz HTML → Ctrl+P → Zapisz jako PDF")
    print(f"\n💾 Wszystkie raporty: {get_report_dir()}")
