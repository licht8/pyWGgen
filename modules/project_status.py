#!/usr/bin/env python3
# modules/project_status.py
# Модуль для отображения состояния проекта wg_qr_generator

import os
import json
import subprocess
import platform
import psutil
from datetime import datetime


def get_external_ip():
    """Получает внешний IP-адрес."""
    try:
        return subprocess.check_output(["curl", "-s", "https://ipinfo.io/ip"], text=True).strip()
    except subprocess.CalledProcessError:
        return "N/A"


def get_open_ports():
    """Возвращает список открытых портов в firewalld."""
    try:
        output = subprocess.check_output(["sudo", "firewall-cmd", "--list-ports"], text=True)
        return output.strip() if output else "Нет открытых портов"
    except subprocess.CalledProcessError:
        return "Ошибка получения данных"


def get_wireguard_status():
    """Возвращает статус WireGuard."""
    try:
        output = subprocess.check_output(["systemctl", "is-active", "wg-quick@wg0"], text=True).strip()
        return "активен" if output == "active" else "неактивен"
    except subprocess.CalledProcessError:
        return "не установлен"


def get_wireguard_peers():
    """Получает список активных пиров WireGuard."""
    try:
        output = subprocess.check_output(["wg", "show"], text=True).splitlines()
        peers = [line.split(":")[1].strip() for line in output if line.startswith("peer:")]
        return peers if peers else "Нет активных пиров"
    except subprocess.CalledProcessError:
        return "Ошибка получения данных"


def get_users_data():
    """Получает информацию о пользователях из user_records.json."""
    user_records_path = os.path.join("user", "data", "user_records.json")
    try:
        with open(user_records_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return "Файл user_records.json отсутствует или поврежден."


def get_gradio_status(port=7860):
    """Проверяет статус Gradio."""
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        cmdline = proc.info.get("cmdline", [])
        if cmdline and "python" in proc.info["name"] and f"{port}" in " ".join(cmdline):
            return f"запущен (PID {proc.info['pid']})"
    return "не запущен"



def show_project_status():
    """Отображает состояние проекта."""
    print("\n=== Информация о состоянии проекта ===\n")

    # Информация о системе
    print(f" 🖥️  ОС: {platform.system()} {platform.release()}")
    print(f" 🧰  Ядро: {platform.uname().release}")
    print(f" 🌍  Внешний IP-адрес: {get_external_ip()}")
    print(f" 🔓  Открытые порты: {get_open_ports()}\n")

    # Состояние WireGuard
    print(f" 🛡️  WireGuard статус: {get_wireguard_status()}")
    print(f" ⚙️  Файл конфигурации: {'/etc/wireguard/wg0.conf' if os.path.exists('/etc/wireguard/wg0.conf') else 'отсутствует'}")
    print(f" 🌐  Активные peers: {get_wireguard_peers()}\n")

    # Пользователи
    users = get_users_data()
    if isinstance(users, dict):
        print(" 👤  Пользователи WireGuard:")
        for user, details in users.items():
            print(f"    - {user}: {details.get('allowed_ips', 'N/A')} | Статус: {details.get('status', 'N/A')}")
    else:
        print(f" 👤  Пользователи: {users}\n")

    # Gradio
    print(f" 🌐  Gradio интерфейс: {get_gradio_status()}")
    print(f" 🔌  Порт Gradio: {'7860 открыт' if '7860/tcp' in get_open_ports() else 'закрыт'}\n")

    # Последний отчет
    report_path = os.path.join("wg_qr_generator", "test_report.txt")
    if os.path.exists(report_path):
        print(f" 📋  Последний отчет: {report_path}")
    else:
        print(" 📋  Последний отчет: отсутствует\n")

    print("=======================================\n")


if __name__ == "__main__":
    show_project_status()
