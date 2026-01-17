#!/usr/bin/env python3
"""Утилиты для AI Assistant."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import subprocess
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings


def get_log_dir() -> Path:
    """Получить директорию для AI логов."""
    log_dir = Path(settings.AI_ASSISTANT_LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def run_cmd(cmd: str, timeout: int = 30) -> str:
    """Выполнить shell команду и вернуть результат."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return f"Error: Command timeout after {timeout}s"
    except Exception as e:
        return f"Error: {str(e)}"


def check_ollama(host: str) -> bool:
    """Проверка доступности Ollama API."""
    try:
        response = requests.get(f"{host}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def save_json_log(data: Dict[str, Any], prefix: str = "diag") -> str:
    """Сохранить JSON лог."""
    log_dir = get_log_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{prefix}_{ts}.json"
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return str(log_file)


def load_json_log(log_file: str) -> Dict[str, Any]:
    """Загрузить JSON лог."""
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


def get_latest_log(prefix: str = "diag") -> str:
    """Получить путь к последнему логу."""
    log_dir = get_log_dir()
    logs = sorted(log_dir.glob(f"{prefix}_*.json"), reverse=True)
    
    if logs:
        return str(logs[0])
    return None
