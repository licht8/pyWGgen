#!/usr/bin/env python3
# gradio_admin/tabs/command_line_tab.py
# Вкладка для эмуляции терминала и запуска команд, включая запуск проекта.

import gradio as gr
import subprocess
from pathlib import Path

console_history = []  # История команд и вывода

def run_command(command):
    """Выполняет команду в терминале и возвращает её результат."""
    global console_history
    try:
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout.strip() or result.stderr.strip()
        console_history.append(f"$ {command}\n{output}")
    except Exception as e:
        console_history.append(f"$ {command}\nОшибка: {str(e)}")
    return "\n".join(console_history[-10:])  # Показываем последние 10 команд


def run_project():
    """Функция для запуска проекта."""
    global console_history
    try:
        # Путь к корневой директории проекта
        project_dir = Path(__file__).resolve().parent.parent.parent
        run_script = project_dir / "run_project.sh"

        if not run_script.exists():
            return "❌ Скрипт run_project.sh не найден."

        # Выполняем run_project.sh
        result = subprocess.run(
            f"bash {run_script}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_dir  # Запускаем из корневой директории проекта
        )

        # Обработка вывода
        output = result.stdout.strip() or result.stderr.strip()
        console_history.append(f"$ bash run_project.sh\n{output}")
        return "\n".join(console_history[-10:])  # Показываем последние 10 команд

    except Exception as e:
        console_history.append(f"$ bash run_project.sh\nОшибка: {str(e)}")
        return "\n".join(console_history[-10:])


def command_line_tab():
    """Создаёт вкладку для эмуляции терминала."""
    with gr.Blocks():
        command_input = gr.Textbox(label="Команда", placeholder="Введите команду...")
        command_output = gr.Textbox(label="Результат", lines=15, interactive=False)
        run_button = gr.Button("Выполнить команду")

        project_button = gr.Button("Запустить проект")
        project_output = gr.Textbox(label="Вывод запуска проекта", lines=15, interactive=False)

        run_button.click(run_command, inputs=command_input, outputs=command_output)
        project_button.click(run_project, outputs=project_output)
