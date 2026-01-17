#!/usr/bin/env python3
"""Интерактивный режим вопросов AI."""

import json
import os
import sys
import tempfile
from typing import Dict, Any

# Импорт settings из родительской папки
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings

from .utils import run_cmd, check_ollama


def show_server_context(data: Dict[str, Any]):
    """Показать контекст сервера перед началом чата."""
    
    nat = data.get("nat", {})
    fw = data.get("firewalld", {})
    wg_status = data.get("wg_status", {})
    
    # Внешний IP
    external_ip = run_cmd("curl -s ifconfig.me") or "N/A"
    
    # Внутренний IP WireGuard (первый активный интерфейс, кроме wg-mgmt)
    wg_internal_ip = "N/A"
    wg_interface = "N/A"
    for iface, info in wg_status.items():
        if iface == "wg-mgmt":
            continue
        if info.get("service_active"):
            wg_interface = iface
            # Получаем IP интерфейса
            ip_output = run_cmd(f"ip addr show {iface} | grep 'inet ' | awk '{{print $2}}'")
            if ip_output:
                wg_internal_ip = ip_output.split('\n')[0]
            break
    
    # WireGuard порт
    wg_port = fw.get('wg_port', 'N/A')
    
    # Ollama статус
    ollama_status = "🟢 Доступен" if data.get("health", {}).get("ollama_ok") else "🔴 Недоступен"
    
    print("\n" + "=" * 72)
    print("📊 КОНТЕКСТ СЕРВЕРА")
    print("=" * 72)
    print(f"🖥️  Hostname: {data.get('hostname')}")
    print(f"🌐 External IP: {external_ip}")
    print(f"🔧 Uptime: {data.get('uptime')}")
    print()
    print(f"📡 WireGuard Interface: {wg_interface}")
    print(f"🔗 Tunnel IP: {wg_internal_ip}")
    print(f"🔌 Port: {wg_port}")
    print(f"📊 Status: {data.get('wg_active')}/{data.get('wg_total')} активны")
    print()
    print(f"👥 Peers:")
    print(f"   • Активных (подключено): {data.get('peers_active', 0)}")
    print(f"   • Настроено (всего): {data.get('peers_configured', 0)}")
    print(f"   • Пользовательских конфигов: {data.get('user_peer_files', {}).get('total', 0)}")
    print()
    print(f"🔥 Firewalld: {fw.get('active')}")
    print(f"🛡️  NAT: {'🟢 OK' if nat.get('ok') else '🔴 Проблема'}")
    print(f"🤖 Ollama AI: {ollama_status} ({settings.OLLAMA_HOST})")
    print(f"🧠 Model: {settings.MODEL_NAME}")
    print("=" * 72)


def ask_question(data: Dict[str, Any], question: str) -> str:
    """Отправка вопроса в Ollama."""
    
    # Формируем детальный контекст из данных для AI
    nat = data.get("nat", {})
    fw = data.get("firewalld", {})
    wg_status = data.get("wg_status", {})
    
    # Список WireGuard интерфейсов с деталями
    wg_details = []
    for iface, info in wg_status.items():
        if iface == "wg-mgmt":
            continue
        
        status = "активен" if info.get("service_active") else "неактивен"
        peers_count = info.get("peers_active", 0)
        port = info.get("listen_port", "N/A")
        
        # IP интерфейса
        ip_output = run_cmd(f"ip addr show {iface} | grep 'inet ' | awk '{{print $2}}'")
        tunnel_ip = ip_output.split('\n')[0] if ip_output else "N/A"
        
        wg_details.append(f"{iface}: {status}, IP: {tunnel_ip}, Port: {port}, Peers: {peers_count}")
    
    # Внешний IP
    external_ip = run_cmd("curl -s ifconfig.me") or "N/A"
    
    # Формирование контекста для AI
    context = f"""Ты эксперт по WireGuard VPN. У тебя есть полные данные о сервере.

ДАННЫЕ СЕРВЕРА:
Hostname: {data.get('hostname')}
External IP: {external_ip}
Uptime: {data.get('uptime')}

WIREGUARD:
{chr(10).join(wg_details) if wg_details else 'Нет активных интерфейсов'}

PEERS:
- Активных (подключено сейчас): {data.get('peers_active', 0)}
- Настроено (в конфигах): {data.get('peers_configured', 0)}
- Пользовательских файлов: {data.get('user_peer_files', {}).get('total', 0)}

СЕТЬ:
Firewalld: {fw.get('active')}
WG порт открыт: {'Да' if fw.get('wg_port_open') else 'Нет'}
NAT: {'OK' if nat.get('ok') else 'ПРОБЛЕМА'}
NAT причина: {nat.get('reason')}

ВОПРОС ПОЛЬЗОВАТЕЛЯ:
{question}

ПРАВИЛА ОТВЕТА:
- Отвечай кратко и по делу на русском языке
- Используй данные выше для точного ответа
- Если нужна команда - дай готовую команду для копирования
- Игнорируй wg-mgmt (это служебный интерфейс)
- Если данных недостаточно - скажи об этом

ОТВЕТ:"""

    # Формирование запроса
    json_data = {
        "model": settings.MODEL_NAME,
        "prompt": context,
        "stream": False,
        "options": {
            "temperature": settings.CHAT_TEMPERATURE
        }
    }
    
    # Сохранить в временный файл
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.json') as f:
        json.dump(json_data, f)
        temp_file = f.name
    
    try:
        # Curl команда как строка
        cmd = f"curl -s --max-time {settings.CHAT_TIMEOUT} -X POST {settings.OLLAMA_HOST}/api/generate -d @{temp_file}"
        
        result = run_cmd(cmd, timeout=settings.CHAT_TIMEOUT + 10)
        
        # Удаляем временный файл
        os.unlink(temp_file)
        
        if not result or result.startswith("Error"):
            return f"❌ Ошибка запроса: {result}"
        
        # Парсинг ответа
        try:
            response = json.loads(result)
            ai_response = response.get('response', 'Нет ответа')
            return ai_response
        
        except json.JSONDecodeError as e:
            return f"❌ Ошибка парсинга: {str(e)}\nОтвет: {result[:200]}"
    
    except Exception as e:
        # Очистка при ошибке
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        return f"❌ Ошибка: {str(e)}"


def interactive_mode(data: Dict[str, Any]):
    """Интерактивный режим вопросов."""
    
    print("\n💬 AI CHAT - Интерактивный режим")
    print("=" * 72)
    
    # Проверка Ollama
    if not check_ollama(settings.OLLAMA_HOST):
        print("❌ Ollama недоступен")
        print(f"   Проверь: {settings.OLLAMA_HOST}")
        print("=" * 72)
        return
    
    # Показываем контекст сервера
    show_server_context(data)
    
    print("\n💡 Задавай вопросы по VPN серверу")
    print("   Для выхода нажми Enter без текста или Ctrl+C\n")
    
    while True:
        try:
            question = input("❓ Вопрос: ").strip()
            
            if not question:
                print("\n👋 Выход из режима вопросов")
                break
            
            print("\n🤖 Ответ:")
            print("-" * 72)
            answer = ask_question(data, question)
            print(answer)
            print("-" * 72 + "\n")
        
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Выход из режима вопросов")
            break
        
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            break
    
    print()
