#!/usr/bin/env python3
# main_interface.py
# Главный интерфейс Gradio для управления проектом wg_qr_generator

import os
import sys
import socket
import gradio as gr
import psutil
import subprocess

# Добавляем путь к корню проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Импортируем вкладки
from gradio_admin.tabs.delete_user_tab import delete_user_tab
from gradio_admin.tabs.statistics_tab import statistics_tab
from gradio_admin.create_user import create_user

USER_RECORDS_JSON = "user/data/user_records.json"
DEFAULT_PORT = 7860

def check_port(port):
    """Проверяет, занят ли порт."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(('0.0.0.0', port)) == 0

def release_port(port):
    """Освобождает занятый порт, если возможно."""
    for proc in psutil.process_iter(attrs=["pid", "name", "connections"]):
        try:
            for conn in proc.info["connections"] or []:
                if conn.laddr.port == port:
                    print(f"🔓 Освобождаем порт {port}, завершая процесс PID {proc.info['pid']}.")
                    proc.terminate()
                    proc.wait(timeout=3)
                    return
        except Exception as e:
            print(f"⚠️ Не удалось завершить процесс: {e}")

def ensure_port_available(port):
    """Убедиться, что порт доступен, или освободить его."""
    if check_port(port):
        print(f"⚠️ Порт {port} уже занят.")
        release_port(port)
        if check_port(port):
            raise RuntimeError(f"❌ Порт {port} не удалось освободить. Попробуйте вручную.")

def save_user_to_json(username, allowed_ips):
    """Сохраняет нового пользователя в user_records.json."""
    if not os.path.exists(USER_RECORDS_JSON):
        records = {}
    else:
        with open(USER_RECORDS_JSON, "r") as file:
            records = json.load(file)

    records[username] = {"allowed_ips": allowed_ips, "status": "active"}
    with open(USER_RECORDS_JSON, "w") as file:
        json.dump(records, file, indent=4)

    print(f"✅ Пользователь {username} добавлен в JSON.")

# Основной интерфейс
with gr.Blocks(css="style.css") as admin_interface:
    # Вкладка для создания пользователя
    with gr.Tab("🌱 Create"):
        with gr.Row():
            gr.Markdown("## Create a new user")
        with gr.Column(scale=1, min_width=300):
            username_input = gr.Textbox(label="Username", placeholder="Enter username...")
            allowed_ips_input = gr.Textbox(label="Allowed IPs", placeholder="Enter allowed IPs...")
            create_button = gr.Button("Create User")
            create_output = gr.Textbox(label="Result", interactive=False)
            qr_code_image = gr.Image(label="QR Code", visible=False)

            def handle_create_user(username, allowed_ips):
                """Обработчик для создания пользователя и отображения QR-кода."""
                result, qr_code_path = create_user(username)
                save_user_to_json(username, allowed_ips)
                if qr_code_path:
                    return result, gr.update(visible=True, value=qr_code_path)
                return result, gr.update(visible=False)

            create_button.click(
                handle_create_user,
                inputs=[username_input, allowed_ips_input],
                outputs=[create_output, qr_code_image]
            )

    # Вкладка для удаления пользователей
    delete_user_tab()

    # Вкладка для статистики пользователей WireGuard
    statistics_tab()

if __name__ == "__main__":
    try:
        print(f"🔍 Проверяем доступность порта {DEFAULT_PORT}...")
        ensure_port_available(DEFAULT_PORT)
        print(f"✅ Порт {DEFAULT_PORT} доступен. Запуск Gradio.")
        admin_interface.launch(server_name="0.0.0.0", server_port=DEFAULT_PORT, share=True)
    except RuntimeError as e:
        print(f"❌ Ошибка: {e}")
    except KeyboardInterrupt:
        print("👋 Завершение работы. До свидания!")
