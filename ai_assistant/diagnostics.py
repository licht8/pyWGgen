#!/usr/bin/env python3
"""Główny skrypt diagnostyki VPN."""

import os
import sys
from pathlib import Path

# Dodajemy katalog główny do ścieżki
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings

from ai_assistant.data_collector import collect_all_data
from ai_assistant.ai_analyzer import analyze_with_ai, interactive_question
from ai_assistant.utils import save_json_log


def print_summary(data: dict):
    """Wyświetla podsumowanie diagnostyki w czytelny sposób."""
    
    nat = data.get("nat", {})
    fw = data.get("firewalld", {})
    wg_status = data.get("wg_status", {})
    
    # Ikonki statusów
    nat_icon = "🟢" if nat.get("ok") else "🔴"
    fw_status = fw.get("active", "nieznany")
    fw_icon = "🟢" if fw_status in ["running", "active"] else "🔴"
    wg_port_icon = "🟢" if fw.get("wg_port_open") else "🔴"
    ollama_icon = "🟢" if data.get("health", {}).get("ollama_ok") else "🔴"
    
    # Interfejsy WireGuard
    wg_lines = []
    for iface, info in wg_status.items():
        status_icon = "🟢" if info.get("service_active") else "🔴"
        wg_lines.append(f"  {status_icon} {iface} ({info.get('service_status')})")
    
    # Wyświetlanie
    print("\n" + "=" * 72)
    print(f"🖥️  {data.get('hostname')} | {data.get('timestamp')}")
    print()
    print(f"📡 WireGuard: {data.get('wg_active')}/{data.get('wg_total')} aktywnych")
    for line in wg_lines:
        print(line)
    print()
    print(f"🔥 Firewalld: {fw_status} | Port WG: {wg_port_icon}")
    print(f"   NAT: {nat_icon}")
    print(f"   {nat.get('reason', 'Brak danych')}")
    print()
    print(f"📁 Peers: {data.get('peers_active', 0)} aktywnych | {data.get('peers_configured', 0)} skonfigurowanych | {data.get('user_peer_files', {}).get('total', 0)} użytkowników")
    print(f"🤖 Ollama: {ollama_icon}")
    print("=" * 72)


def main():
    """Funkcja główna."""
    
    print("\n🚀 Uruchamianie diagnostyki AI VPN...")
    
    # Zbieranie danych
    print("🔄 Zbieranie danych...")
    data = collect_all_data()
    
    # Zapis logu
    log_file = save_json_log(data, prefix="diag")
    print(f"💾 Log: {log_file}")
    
    # Wyświetlenie podsumowania
    print_summary(data)
    
    # Analiza AI
    print("\n🤖 ANALIZA AI:")
    print("=" * 72)
    
    from ai_assistant.utils import check_ollama
    if not check_ollama(settings.OLLAMA_HOST):
        print("❌ Ollama niedostępny")
        print(f"   Sprawdź: {settings.OLLAMA_HOST}")
        print("=" * 72)
    else:
        ai_response = analyze_with_ai(data)
        # Odpowiedź jest już wyświetlana w analyze_with_ai
    
    # Zakończenie
    print("\n✅ Diagnostyka zakończona!")
    print(f"📄 Szczegółowy raport: {log_file}")
    print()


if __name__ == "__main__":
    main()
