#!/usr/bin/env python3
# gradio_admin/tabs/command_line_tab.py
# Вкладка для эмуляции командной строки и запуска проекта

import gradio as gr
import subprocess
from pathlib import Path

def create_command_line_tab():
    """
    Создает вкладку для эмуляции командной строки.
    """
    console_history = []

    def handle_command(command):
        """Обработчик ввода команды."""
        nonlocal console_history
        if command.strip() == "":
            return "\n".join(console_history)

        try:
            # Выполняем команду
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stdout.strip() or result.stderr.strip()
            console_history.append(f"$ {command}\n{output}")
        except Exception as e:
            console_history.append(f"$ {command}\nОшибка: {str(e)}")

        # Оставляем последние 20 команд
        console_history = console_history[-20:]
        return "\n".join(console_history)

    def run_project():
        """Функция для запуска проекта через специальный скрипт."""
        try:
            project_dir = Path(__file__).resolve().parent.parent.parent
            run_script = project_dir / "run_project.sh"

            if not run_script.exists():
                return "❌ Скрипт run_project.sh не найден."

            result = subprocess.run(f"bash {run_script}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=project_dir)
            output = result.stdout.strip() or result.stderr.strip()
            console_history.append(f"$ bash run_project.sh\n{output}")
            return "\n".join(console_history)
        except Exception as e:
            console_history.append(f"$ bash run_project.sh\nОшибка: {str(e)}")
            return "\n".join(console_history)

    # Интерфейс
    command_input = gr.Textbox(label="Введите команду", placeholder="Пример: ls -l", lines=1)
    console_output = gr.Textbox(label="Консольный вывод", value="", interactive=False, lines=15)
    execute_button = gr.Button("Выполнить команду")
    run_project_button = gr.Button("Запустить проект")

    execute_button.click(
        handle_command,
        inputs=command_input,
        outputs=console_output,
    )

    run_project_button.click(
        run_project,
        outputs=console_output,
    )

    return [command_input, console_output, execute_button, run_project_button]
