#!/usr/bin/env python3
"""Главный скрипт диагностики VPN."""

import os
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings

from ai_assistant.data_collector import collect_all_data
from ai_assistant.ai_analyzer import analyze_with_ai, interactive_question
from ai_assistant.utils import save_json_log


def print_summary(data: dict):
    """Красивый вывод summary диагностики."""
    
    nat = data.get("nat", {})
    fw = data.get("firewalld", {})
    wg_status = data.get("wg_status", {})
    
    # Иконки статусов
    nat_icon = "🟢" if nat.get("ok") else "🔴"
    fw_status = fw.get("active", "unknown")
    fw_icon = "🟢" if fw_status in ["running", "active"] else "🔴"
    wg_port_icon = "🟢" if fw.get("wg_port_open") else "🔴"
    ollama_icon = "🟢" if data.get("health", {}).get("ollama_ok") else "🔴"
    
    # WireGuard интерфейсы
    wg_lines = []
    for iface, info in wg_status.items():
        status_icon = "🟢" if info.get("service_active") else "🔴"
        wg_lines.append(f"  {status_icon} {iface} ({info.get('service_status')})")
    
    # Вывод
    print("\n" + "=" * 72)
    print(f"🖥️  {data.get('hostname')} | {data.get('timestamp')}")
    print()
    print(f"📡 WireGuard: {data.get('wg_active')}/{data.get('wg_total')} активны")
    for line in wg_lines:
        print(line)
    print()
    print(f"🔥 Firewalld: {fw_status} | WG порт: {wg_port_icon}")
    print(f"   NAT: {nat_icon}")
    print(f"   {nat.get('reason', 'Нет данных')}")
    print()
    print(f"📁 Peers: {data.get('peers_active', 0)} активных | {data.get('peers_configured', 0)} настроено | {data.get('user_peer_files', {}).get('total', 0)} пользовательских")
    print(f"🤖 Ollama: {ollama_icon}")
    print("=" * 72)


def main():
    """Главная функция."""
    
    print("\n🚀 Запуск AI VPN Diagnostics...")
    
    # Сбор данных
    print("🔄 Сбор данных...")
    data = collect_all_data()
    
    # Сохранение лога
    log_file = save_json_log(data, prefix="diag")
    print(f"💾 Лог: {log_file}")
    
    # Вывод summary
    print_summary(data)
    
    # AI анализ
    print("\n🤖 АНАЛИЗ AI:")
    print("=" * 72)
    
    from ai_assistant.utils import check_ollama
    if not check_ollama(settings.OLLAMA_HOST):
        print("❌ Ollama недоступен")
        print(f"   Проверь: {settings.OLLAMA_HOST}")
        print("=" * 72)
    else:
        ai_response = analyze_with_ai(data)
        # Ответ уже выводится внутри analyze_with_ai
    
    # Завершение
    print("\n✅ Диагностика завершена!")
    print(f"📄 Подробный отчёт: {log_file}")
    print()


if __name__ == "__main__":
    main()
