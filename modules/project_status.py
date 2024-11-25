#!/usr/bin/env python3
# modules/project_status.py
# Модуль для отображения состояния проекта wg_qr_generator

import os
import json
import subprocess
import platform
import psutil
from datetime import datetime
from termcolor import colored


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
        if output == "active":
            return colored("активен ✅", "green")
        else:
            return colored("неактивен ❌", "red")
    except subprocess.CalledProcessError:
        return colored("не установлен ❌", "red")


def get_wireguard_peers():
    """Получает список активных пиров WireGuard."""
    try:
        output = subprocess.check_output(["wg", "show"], text=True).splitlines()
        peers = [line.split(":")[1].strip() for line in output if line.startswith("peer:")]
        if peers:
            return ", ".join(peers)
        return colored("Нет активных пиров ❌", "red")
    except subprocess.CalledProcessError:
        return colored("Ошибка получения данных ❌", "red")


def get_users_data():
    """Получает информацию о пользователях из user_records.json."""
    user_records_path = os.path.join("user", "data", "user_records.json")
    try:
        with open(user_records_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return colored("Файл user_records.json отсутствует или поврежден ❌", "red")


def get_gradio_status(port=7860):
    """Проверяет статус Gradio."""
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        cmdline = proc.info.get("cmdline", [])
        if cmdline and "python" in proc.info["name"] and f"{port}" in " ".join(cmdline):
            return colored(f"запущен ✅ (PID {proc.info['pid']})", "green")
    return colored("не запущен ❌", "red")


def get_gradio_port_status(port=7860):
    """Проверяет, открыт ли порт Gradio."""
    open_ports = get_open_ports()
    if f"{port}/tcp" in open_ports:
        return colored("открыт ✅", "green")
    return colored("закрыт ❌", "red")


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
    print(f" ⚙️  Файл конфигурации: {'/etc/wireguard/wg0.conf' if os.path.exists('/etc/wireguard/wg0.conf') else colored('отсутствует ❌', 'red')}")
    print(f" 🌐 Активные peers: {get_wireguard_peers()}\n")

    # Пользователи
    users = get_users_data()
    if isinstance(users, dict):
        print(" 👤  Пользователи WireGuard:")
        for user, details in users.items():
            status = details.get("status", "N/A")
            status_colored = colored(status, "green") if status == "active" else colored(status, "red")
            print(f"    - {user}: {details.get('allowed_ips', 'N/A')} | Статус: {status_colored}")
    else:
        print(f" 👤  Пользователи: {users}\n")

    # Gradio
    print(f" 🌐  Gradio интерфейс: {get_gradio_status()}")
    print(f" 🔌  Порт Gradio: {get_gradio_port_status()}\n")

    # Последний отчет
    report_path = os.path.join("wg_qr_generator", "test_report.txt")
    if os.path.exists(report_path):
        print(f" 📋  Последний отчет: {report_path}")
    else:
        print(colored(" 📋  Последний отчет: отсутствует ❌", "red"))

    print("\n===========================================\n")


if __name__ == "__main__":
    show_project_status()
