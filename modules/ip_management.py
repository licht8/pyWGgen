import os
import json
import settings

IP_DB_PATH = "user/data/ip_records.json"  # Новый файл для записи занятых IP-адресов

def get_existing_ips(config_file):
    """Получает IP-адреса из конфигурации сервера, добавляет их в базу"""
    existing_ips = set()
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            for line in file:
                if line.startswith('AllowedIPs'):
                    parts = line.split('=')
                    if len(parts) > 1:
                        addresses = parts[1].strip().split(',')
                        for address in addresses:
                            ip = address.split('/')[0].strip()
                            existing_ips.add(ip)
    return existing_ips

def load_ip_records():
    if os.path.exists(settings.IP_DB_PATH):
        with open(settings.IP_DB_PATH, 'r') as file:
            return json.load(file)
    return {}

def save_ip_records(ip_records):
    with open(settings.IP_DB_PATH, 'w') as file:
        json.dump(ip_records, file, indent=4)

def generate_ip(existing_ips, subnet="10.66.66.0"):
    """Генерирует новый IP-адрес, основываясь на указанной подсети."""
    base_ip = ipaddress.IPv4Network(subnet, strict=False)
    for ip in base_ip.hosts():
        if str(ip) not in existing_ips:
            return f"{ip}/32", str(ip)
    raise RuntimeError("Нет доступных IP-адресов в подсети.")


def release_ip(ip):
    """
    Освобождает IP-адрес, делая его доступным для повторного использования.
    """
    ip_records = load_ip_records()
    if ip in ip_records:
        if ip_records[ip]:  # Проверяем, что IP действительно занят
            print(f"Освобождение IP-адреса: {ip}")
            ip_records[ip] = False  # Помечаем IP как свободный
            save_ip_records(ip_records)  # Сохраняем изменения
        else:
            print(f"IP-адрес {ip} уже был помечен как свободный.")
    else:
        print(f"IP-адрес {ip} не найден в базе для освобождения.")
