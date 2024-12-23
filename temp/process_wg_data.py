#!/usr/bin/env python3
# process_wg_data.py
# ==================================================
# Скрипт для обработки сырого вывода данных WireGuard.
# Версия: 1.0 (2024-12-21)
# ==================================================
# Описание:
# Обрабатывает файл `wg_raw_data.txt` и извлекает структурированную
# информацию о сервере и пользователях.
# ==================================================

import re
from pathlib import Path

def process_wg_data(input_file, output_file):
    """
    Обрабатывает сырой файл данных WireGuard и создает структурированный отчет.
    
    Args:
        input_file (str): Путь к исходному файлу данных.
        output_file (str): Путь к файлу, куда будет записан результат.
    """
    try:
        with open(input_file, 'r') as f:
            raw_data = f.read()
        
        report = []
        
        # Парсим информацию о сервере
        server_info = re.search(r"\[Interface\](.*?)### Client", raw_data, re.DOTALL)
        if server_info:
            report.append("=== Server Configuration ===\n")
            report.append(server_info.group(1).strip() + "\n")
        
        # Парсим информацию о клиентах
        clients_info = re.findall(r"### Client (.*?)\[Peer\](.*?)\n\n", raw_data, re.DOTALL)
        if clients_info:
            report.append("\n=== Clients ===\n")
            for client in clients_info:
                client_name, client_data = client
                report.append(f"Client: {client_name.strip()}\n{client_data.strip()}\n")
        
        # Парсим информацию о статусе WireGuard
        wg_status = re.search(r"\[WireGuard Status.*?\](.*)", raw_data, re.DOTALL)
        if wg_status:
            report.append("\n=== WireGuard Status ===\n")
            report.append(wg_status.group(1).strip() + "\n")
        
        # Парсим параметры
        params = re.search(r"\[WireGuard Parameters File\](.*)", raw_data, re.DOTALL)
        if params:
            report.append("\n=== WireGuard Parameters ===\n")
            report.append(params.group(1).strip() + "\n")
        
        # Сохраняем отчет
        with open(output_file, 'w') as f:
            f.writelines(report)
        
        print(f"Processed data has been saved to {output_file}")
    
    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    input_file = "wg_raw_data.txt"
    output_file = "wg_processed_report.txt"
    process_wg_data(input_file, output_file)
