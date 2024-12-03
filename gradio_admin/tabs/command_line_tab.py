#!/usr/bin/env python3
# gradio_admin/tabs/command_line_tab.py
# Вкладка для эмуляции терминала и запуска команд, включая запуск проекта, с поддержкой логирования.

import gradio as gr
import subprocess
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # Уровень отладки
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("gradio_terminal_debug.log"),  # Логи записываются в файл
        logging.StreamHandler()  # Логи выводятся в консоль
    ]
)
logger = logging.getLogger(__name__)

console_history = []  # История команд и вывода


def run_command(command):
    """Выполняет команду в терминале и возвращает её результат."""
    global console_history
    try:
        logger.debug(f"Выполнение команды: {command}")
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout.strip() or result.stderr.strip()
        console_history.append(f"$ {command}\n{output}")
        logger.info(f"Результат команды:\n{output}")
    except Exception as e:
        error_message = f"Ошибка выполнения команды '{command}': {str(e)}"
        console_history.append(f"$ {command}\nОшибка: {error_message}")
        logger.error(error_message)
    return "\n".join(console_history[-10:])  # Показываем последние 10 команд


def run_project():
    """Функция для запуска проекта."""
    global console_history
    try:
        project_dir = Path(__file__).resolve().parent.parent.parent
        run_script = project_dir / "run_project.sh"

        if not run_script.exists():
            error_message = "❌ Скрипт run_project.sh не найден."
            console_history.append(error_message)
            logger.error(error_message)
            return "\n".join(console_history[-10:])

        logger.debug(f"Запуск скрипта: {run_script} из директории {project_dir}")
        result = subprocess.run(
            f"bash {run_script}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_dir
        )

        output = result.stdout.strip() or result.stderr.strip()
        console_history.append(f"$ bash run_project.sh\n{output}")
        logger.info(f"Результат запуска проекта:\n{output}")
        return "\n".join(console_history[-10:])

    except Exception as e:
        error_message = f"Ошибка запуска проекта: {str(e)}"
        console_history.append(f"$ bash run_project.sh\nОшибка: {error_message}")
        logger.error(error_message)
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
