#!/usr/bin/env python3
"""Tryb interaktywny pytań do AI."""

import json
import os
import sys
import tempfile
from typing import Dict, Any

# Import settings z katalogu nadrzędnego
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings

from .utils import run_cmd, check_ollama


def show_server_context(data: Dict[str, Any]):
    """Pokazuje kontekst serwera przed rozpoczęciem czatu."""
    
    nat = data.get("nat", {})
    fw = data.get("firewalld", {})
    wg_status = data.get("wg_status", {})
    
    # Zewnętrzny IP
    external_ip = run_cmd("curl -s ifconfig.me") or "N/A"
    
    # Wewnętrzny IP WireGuard (pierwszy aktywny interfejs, oprócz wg-mgmt)
    wg_internal_ip = "N/A"
    wg_interface = "N/A"
    for iface, info in wg_status.items():
        if iface == "wg-mgmt":
            continue
        if info.get("service_active"):
            wg_interface = iface
            # Pobierz IP interfejsu
            ip_output = run_cmd(f"ip addr show {iface} | grep 'inet ' | awk '{{print $2}}'")
            if ip_output:
                wg_internal_ip = ip_output.split('\n')[0]
            break
    
    # Port WireGuard
    wg_port = fw.get('wg_port', 'N/A')
    
    # Status Ollama
    ollama_status = "🟢 Dostępny" if data.get("health", {}).get("ollama_ok") else "🔴 Niedostępny"
    
    print("\n" + "=" * 72)
    print("📊 KONTEXT SERWERA")
    print("=" * 72)
    print(f"🖥️  Hostname: {data.get('hostname')}")
    print(f"🌐 Zewnętrzny IP: {external_ip}")
    print(f"🔧 Czas pracy: {data.get('uptime')}")
    print()
    print(f"📡 Interfejs WireGuard: {wg_interface}")
    print(f"🔗 IP tunelu: {wg_internal_ip}")
    print(f"🔌 Port: {wg_port}")
    print(f"📊 Status: {data.get('wg_active')}/{data.get('wg_total')} aktywnych")
    print()
    print(f"👥 Peers:")
    print(f"   • Aktywnych (połączonych): {data.get('peers_active', 0)}")
    print(f"   • Skonfigurowanych (łącznie): {data.get('peers_configured', 0)}")
    print(f"   • Plików konfiguracyjnych użytkowników: {data.get('user_peer_files', {}).get('total', 0)}")
    print()
    print(f"🔥 Firewalld: {fw.get('active')}")
    print(f"🛡️  NAT: {'🟢 OK' if nat.get('ok') else '🔴 Problem'}")
    print(f"🤖 Ollama AI: {ollama_status} ({settings.OLLAMA_HOST})")
    print(f"🧠 Model: {settings.MODEL_NAME}")
    print("=" * 72)


def ask_question(data: Dict[str, Any], question: str) -> str:
    """Wysyła pytanie do Ollama."""
    
    # Tworzymy szczegółowy kontekst z danych dla AI
    nat = data.get("nat", {})
    fw = data.get("firewalld", {})
    wg_status = data.get("wg_status", {})
    
    # Lista interfejsów WireGuard z szczegółami
    wg_details = []
    for iface, info in wg_status.items():
        if iface == "wg-mgmt":
            continue
        
        status = "aktywny" if info.get("service_active") else "nieaktywny"
        peers_count = info.get("peers_active", 0)
        port = info.get("listen_port", "N/A")
        
        # IP interfejsu
        ip_output = run_cmd(f"ip addr show {iface} | grep 'inet ' | awk '{{print $2}}'")
        tunnel_ip = ip_output.split('\n')[0] if ip_output else "N/A"
        
        wg_details.append(f"{iface}: {status}, IP: {tunnel_ip}, Port: {port}, Peers: {peers_count}")
    
    # Zewnętrzny IP
    external_ip = run_cmd("curl -s ifconfig.me") or "N/A"
    
    # Tworzenie kontekstu dla AI
    context = f"""Jesteś ekspertem WireGuard VPN. Masz pełne dane o serwerze.

DANE SERWERA:
Hostname: {data.get('hostname')}
Zewnętrzny IP: {external_ip}
Czas pracy: {data.get('uptime')}

WIREGUARD:
{chr(10).join(wg_details) if wg_details else 'Brak aktywnych interfejsów'}

PEERS:
- Aktywnych (połączonych teraz): {data.get('peers_active', 0)}
- Skonfigurowanych (w konfiguracjach): {data.get('peers_configured', 0)}
- Plików użytkowników: {data.get('user_peer_files', {}).get('total', 0)}

SIEĆ:
Firewalld: {fw.get('active')}
Port WG otwarty: {'Tak' if fw.get('wg_port_open') else 'Nie'}
NAT: {'OK' if nat.get('ok') else 'PROBLEM'}
Przyczyna NAT: {nat.get('reason')}

PYTANIE UŻYTKOWNIKA:
{question}

ZASADY ODPOWIEDZI:
- Odpowiadaj krótko i konkretnie po polsku
- Używaj powyższych danych do precyzyjnej odpowiedzi
- Jeśli potrzebna komenda - podaj gotową komendę do skopiowania
- Ignoruj wg-mgmt (to interfejs służbowy)
- Jeśli danych za mało - powiedz o tym

ODPOWIEDŹ:"""

    # Tworzenie zapytania
    json_data = {
        "model": settings.MODEL_NAME,
        "prompt": context,
        "stream": False,
        "options": {
            "temperature": settings.CHAT_TEMPERATURE
        }
    }
    
    # Zapis do pliku tymczasowego
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.json') as f:
        json.dump(json_data, f)
        temp_file = f.name
    
    try:
        # Komenda curl jako string
        cmd = f"curl -s --max-time {settings.CHAT_TIMEOUT} -X POST {settings.OLLAMA_HOST}/api/generate -d @{temp_file}"
        
        result = run_cmd(cmd, timeout=settings.CHAT_TIMEOUT + 10)
        
        # Usuń plik tymczasowy
        os.unlink(temp_file)
        
        if not result or result.startswith("Error"):
            return f"❌ Błąd zapytania: {result}"
        
        # Parsowanie odpowiedzi
        try:
            response = json.loads(result)
            ai_response = response.get('response', 'Brak odpowiedzi')
            return ai_response
        
        except json.JSONDecodeError as e:
            return f"❌ Błąd parsowania: {str(e)}\nOdpowiedź: {result[:200]}"
    
    except Exception as e:
        # Czyszczenie przy błędzie
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        return f"❌ Błąd: {str(e)}"


def interactive_mode(data: Dict[str, Any]):
    """Tryb interaktywny pytań."""
    
    print("\n💬 CZAT AI - Tryb interaktywny")
    print("=" * 72)
    
    # Sprawdzenie Ollama
    if not check_ollama(settings.OLLAMA_HOST):
        print("❌ Ollama niedostępny")
        print(f"   Sprawdź: {settings.OLLAMA_HOST}")
        print("=" * 72)
        return
    
    # Pokazujemy kontekst serwera
    show_server_context(data)
    
    print("\n💡 Zadawaj pytania dotyczące serwera VPN")
    print("   Aby wyjść naciśnij Enter bez tekstu lub Ctrl+C\n")
    
    while True:
        try:
            question = input("❓ Pytanie: ").strip()
            
            if not question:
                print("\n👋 Wyjście z trybu pytań")
                break
            
            print("\n🤖 Odpowiedź:")
            print("-" * 72)
            answer = ask_question(data, question)
            print(answer)
            print("-" * 72 + "\n")
        
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Wyjście z trybu pytań")
            break
        
        except Exception as e:
            print(f"\n❌ Błąd: {e}")
            break
    
    print()
