#!/usr/bin/env python3
"""AI анализатор для диагностики VPN."""

import json
import os
import sys
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings

from .utils import run_cmd, check_ollama


def prepare_prompt(data: Dict[str, Any]) -> str:
    """Подготовка промпта для AI анализа."""
    
    nat = data.get("nat", {})
    fw = data.get("firewalld", {})
    wg_status = data.get("wg_status", {})
    
    # Список интерфейсов
    wg_interfaces = []
    for iface, info in wg_status.items():
        status = "активен" if info.get("service_active") else "неактивен"
        wg_interfaces.append(f"{iface} ({status})")
    
    prompt = f"""Ты эксперт по WireGuard VPN. Проанализируй диагностику и дай краткий структурированный ответ.

СОСТОЯНИЕ СИСТЕМЫ:
- Сервер: {data.get('hostname')}
- WireGuard интерфейсы: {', '.join(wg_interfaces)}
- Firewalld: {fw.get('active')}
- WG порт открыт: {'Да' if fw.get('wg_port_open') else 'Нет'}
- NAT: {'OK' if nat.get('ok') else 'ПРОБЛЕМА'}
- NAT причина: {nat.get('reason')}
- IP Forwarding: {'Включён' if nat.get('ip_forward') else 'Выключен'}
- Peers активных: {data.get('peers_active', 0)}
- Peers настроено: {data.get('peers_configured', 0)}
- Пользовательских конфигов: {data.get('user_peer_files', {}).get('total', 0)}

ФОРМАТ ОТВЕТА:
🟢 Статус: [OK/WARNING/ERROR] | Оценка: [0-100]/100

📝 [Краткое описание состояния системы в 1-2 предложениях]

✅ Работает:
• [Что работает правильно]
• [Что настроено корректно]

{'⚠️ Проблемы:' if not nat.get('ok') or data.get('wg_active', 0) < data.get('wg_total', 0) else '✨ Всё в порядке! Система работает корректно.'}

Дай анализ:"""
    
    return prompt


def analyze_with_ai(data: Dict[str, Any]) -> str:
    """Анализ данных с помощью AI."""
    
    # Подготовка промпта
    prompt = prepare_prompt(data)
    
    # Формирование запроса для curl
    json_data = {
        "model": settings.MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": settings.AI_TEMPERATURE
        }
    }
    
    # Сохранить в временный файл для curl
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(json_data, f)
        temp_file = f.name
    
    try:
        # Curl команда
        cmd = f"curl -s -X POST {settings.OLLAMA_HOST}/api/generate -d @{temp_file}"
        
        print("🔄 Запрос к AI...")
        result = run_cmd(cmd, timeout=settings.AI_TIMEOUT)
        
        # Очистка временного файла
        os.unlink(temp_file)
        
        if not result or result.startswith("Error"):
            print(f"❌ Ошибка запроса: {result}")
            return "Ошибка запроса к AI"
        
        # Парсинг ответа
        try:
            response = json.loads(result)
            ai_response = response.get('response', 'Нет ответа')
            
            print(ai_response)
            print("=" * 72)
            return ai_response
        
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга JSON: {e}")
            print(f"Ответ: {result[:200]}...")
            return "Ошибка парсинга ответа"
    
    except Exception as e:
        # Очистка при ошибке
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        
        print(f"❌ Ошибка: {e}")
        return f"Ошибка: {str(e)}"


def interactive_question(data: Dict[str, Any], question: str) -> str:
    """Интерактивный вопрос к AI."""
    
    # Контекст из диагностики
    context = f"""КОНТЕКСТ ДИАГНОСТИКИ:
- WireGuard: {data.get('wg_active')}/{data.get('wg_total')} активны
- NAT: {'OK' if data.get('nat', {}).get('ok') else 'ПРОБЛЕМА'}
- Firewalld: {data.get('firewalld', {}).get('active')}
- Peers: {data.get('peers_active', 0)} активных, {data.get('peers_configured', 0)} настроено

ВОПРОС ПОЛЬЗОВАТЕЛЯ:
{question}

ОТВЕТ (кратко и по делу):"""
    
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
                return response.get('response', 'Нет ответа')
            except json.JSONDecodeError:
                return "Ошибка парсинга ответа"
        
        return "Ошибка запроса"
    
    except Exception as e:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        return f"Ошибка: {str(e)}"
