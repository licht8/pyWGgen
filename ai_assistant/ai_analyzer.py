#!/usr/bin/env python3
"""Analizator AI dla diagnostyki VPN."""

import json
import os
import sys
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings

from .utils import run_cmd, check_ollama


def prepare_prompt(data: Dict[str, Any]) -> str:
    """Przygotowuje prompt dla analizy AI."""
    
    nat = data.get("nat", {})
    fw = data.get("firewalld", {})
    wg_status = data.get("wg_status", {})
    
    # Lista interfejsów
    wg_interfaces = []
    for iface, info in wg_status.items():
        status = "aktywny" if info.get("service_active") else "nieaktywny"
        wg_interfaces.append(f"{iface} ({status})")
    
    prompt = f"""Jesteś ekspertem WireGuard VPN. Przeanalizuj diagnostykę i podaj krótki strukturalny raport.

STAN SYSTEMU:
- Serwer: {data.get('hostname')}
- Interfejsy WireGuard: {', '.join(wg_interfaces)}
- Firewalld: {fw.get('active')}
- Port WG otwarty: {'Tak' if fw.get('wg_port_open') else 'Nie'}
- NAT: {'OK' if nat.get('ok') else 'PROBLEM'}
- Przyczyna NAT: {nat.get('reason')}
- IP Forwarding: {'Włączony' if nat.get('ip_forward') else 'Wyłączony'}
- Aktywne Peers: {data.get('peers_active', 0)}
- Skonfigurowane Peers: {data.get('peers_configured', 0)}
- Konfiguracji użytkowników: {data.get('user_peer_files', {}).get('total', 0)}

FORMAT ODPOWIEDZI:
🟢 Status: [OK/OSTRZEŻENIE/BŁĄD] | Ocena: [0-100]/100

📝 [Krótki opis stanu systemu w 1-2 zdaniach]

✅ Działa:
• [Co działa poprawnie]
• [Co jest skonfigurowane prawidłowo]

{'⚠️ Problemy:' if not nat.get('ok') or data.get('wg_active', 0) < data.get('wg_total', 0) else '✨ Wszystko w porządku! System działa poprawnie.'}

Podaj analizę:"""
    
    return prompt


def analyze_with_ai(data: Dict[str, Any]) -> str:
    """Analiza danych za pomocą AI."""
    
    # Przygotowanie promptu
    prompt = prepare_prompt(data)
    
    # Formowanie zapytania dla curl
    json_data = {
        "model": settings.MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": settings.AI_TEMPERATURE
        }
    }
    
    # Zapis do pliku tymczasowego dla curl
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(json_data, f)
        temp_file = f.name
    
    try:
        # Komenda Curl
        cmd = f"curl -s -X POST {settings.OLLAMA_HOST}/api/generate -d @{temp_file}"
        
        print("🔄 Zapytanie do AI...")
        result = run_cmd(cmd, timeout=settings.AI_TIMEOUT)
        
        # Czyszczenie pliku tymczasowego
        os.unlink(temp_file)
        
        if not result or result.startswith("Error"):
            print(f"❌ Błąd zapytania: {result}")
            return "Błąd zapytania do AI"
        
        # Parsowanie odpowiedzi
        try:
            response = json.loads(result)
            ai_response = response.get('response', 'Brak odpowiedzi')
            
            print(ai_response)
            print("=" * 72)
            return ai_response
        
        except json.JSONDecodeError as e:
            print(f"❌ Błąd parsowania JSON: {e}")
            print(f"Odpowiedź: {result[:200]}...")
            return "Błąd parsowania odpowiedzi"
    
    except Exception as e:
        # Czyszczenie przy błędzie
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        
        print(f"❌ Błąd: {e}")
        return f"Błąd: {str(e)}"


def interactive_question(data: Dict[str, Any], question: str) -> str:
    """Interaktywne pytanie do AI."""
    
    # Kontekst z diagnostyki
    context = f"""KONTEXT DIAGNOSTYKI:
- WireGuard: {data.get('wg_active')}/{data.get('wg_total')} aktywnych
- NAT: {'OK' if data.get('nat', {}).get('ok') else 'PROBLEM'}
- Firewalld: {data.get('firewalld', {}).get('active')}
- Peers: {data.get('peers_active', 0)} aktywnych, {data.get('peers_configured', 0)} skonfigurowanych

PYTANIE UŻYTKOWNIKA:
{question}

ODPOWIEDŹ (krótko i konkretnie):"""
    
    # Formowanie zapytania
    json_data = {
        "model": settings.MODEL_NAME,
        "prompt": context,
        "stream": False,
        "options": {
            "temperature": settings.CHAT_TEMPERATURE
        }
    }
    
    # Zapis do pliku tymczasowego
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(json_data, f)
        temp_file = f.name
    
    try:
        cmd = f"curl -s -X POST {settings.OLLAMA_HOST}/api/generate -d @{temp_file}"
        result = run_cmd(cmd, timeout=settings.CHAT_TIMEOUT)
        
        os.unlink(temp_file)
        
        if result and not result.startswith("Error"):
            try:
                response = json.loads(result)
                return response.get('response', 'Brak odpowiedzi')
            except json.JSONDecodeError:
                return "Błąd parsowania odpowiedzi"
        
        return "Błąd zapytania"
    
    except Exception as e:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        return f"Błąd: {str(e)}"
