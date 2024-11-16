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

def generate_ip(existing_ips):
    """Генерирует новый IP-адрес или использует освобожденный, если доступен"""
    ip_records = load_ip_records()
    
    # Используем освобожденные IP, если они есть
    free_ips = [ip for ip, in_use in ip_records.items() if not in_use]
    if free_ips:
        new_ip = free_ips.pop(0)
        ip_records[new_ip] = True  # Помечаем IP как используемый
        save_ip_records(ip_records)
        return f"{new_ip}/32", new_ip

    # Генерируем новый IP, если нет доступных свободных
    base_ipv4 = "10.66.66"
    max_ipv4 = 1
    for ip in existing_ips:
        if ip.startswith(base_ipv4):
            last_octet = int(ip.split('.')[-1])
            if last_octet > max_ipv4:
                max_ipv4 = last_octet
    new_ipv4 = f"{base_ipv4}.{max_ipv4 + 1}"
    ip_records[new_ipv4] = True  # Добавляем новый IP как занятый
    save_ip_records(ip_records)
    
    return f"{new_ipv4}/32", new_ipv4

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
