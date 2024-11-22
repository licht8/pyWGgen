#!/usr/bin/env python3
"""
gradio_admin/wg_interface.py

Gradio-интерфейс для отображения состояния WireGuard:
- Фильтрация активных и неактивных пользователей.
- Отображение трафика, подключения и других данных.
"""

import json
import gradio as gr

JSON_LOG_PATH = "/var/log/wg_users.json"


def load_data(show_inactive):
    """Загружает данные из JSON и фильтрует активных пользователей."""
    with open(JSON_LOG_PATH, "r") as f:
        data = json.load(f)

    users = data.get("users", {})
    table = []

    for username, user_data in users.items():
        if not show_inactive and user_data["status"] == "inactive":
            continue
        table.append([
            username,
            ", ".join(user_data["endpoints"]),
            user_data["allowed_ips"],
            user_data["total_transfer"]["received"],
            user_data["total_transfer"]["sent"],
            user_data["last_handshake"] or "Никогда",
            "Активен" if user_data["status"] == "active" else "Неактивен"
        ])

    return table


def interface():
    """Создает Gradio-интерфейс."""
    with gr.Blocks() as app:
        gr.Markdown("### WireGuard Пользователи")

        show_inactive = gr.Checkbox(label="Показать неактивных пользователей", value=True)
        table = gr.Dataframe(headers=["Пользователь", "Endpoints", "Разрешенные IPs", "Принято", "Отправлено", "Handshake", "Статус"], 
                             interactive=False)
        
        show_inactive.change(fn=load_data, inputs=[show_inactive], outputs=[table])

    app.launch()


if __name__ == "__main__":
    interface()
    admin_interface.launch(server_name="0.0.0.0", server_port=7860, share=True)
