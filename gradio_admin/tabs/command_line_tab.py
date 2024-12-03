#!/usr/bin/env python3
# gradio_admin/tabs/command_line_tab.py
# Вкладка для эмуляции командной строки и запуска проекта

import gradio as gr
import subprocess


def run_command(command, current_history):
    """
    Выполняет команду в терминале и возвращает результат.
    
    :param command: Команда для выполнения.
    :param current_history: История команд.
    :return: Обновленная история команд.
    """
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
        return f"{current_history}\n$ {command}\n{output}"
    except Exception as e:
        return f"{current_history}\n$ {command}\nОшибка: {str(e)}"


def run_project():
    """
    Запускает проект через gradio_cli.py.
    """
    try:
        result = subprocess.run(
            ["python3", "gradio_admin/gradio_cli.py"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        output = result.stdout.strip() or result.stderr.strip()
        return f"$ python3 gradio_admin/gradio_cli.py\n{output}"
    except Exception as e:
        return f"Ошибка запуска проекта: {str(e)}"


def create_command_line_tab():
    """
    Вкладка для эмуляции командной строки и запуска проекта.
    """
    with gr.Row():
        gr.Markdown("### 💻 Эмуляция командной строки")
    
    # Поле для истории команд
    console_output = gr.Textbox(label="Консоль", value="", lines=15, interactive=False)
    
    # Поле ввода команды
    command_input = gr.Textbox(label="Введите команду", placeholder="Введите команду для выполнения...")
    
    # Кнопка для выполнения команды
    execute_button = gr.Button("Выполнить")
    
    # Кнопка для запуска проекта
    run_project_button = gr.Button("Запустить проект")
    
    # Логика обработки команды
    def handle_command(command, history):
        """
        Обрабатывает ввод команды и обновляет историю.
        """
        return run_command(command, history)
    
    # Логика запуска проекта
    def handle_run_project(history):
        """
        Обрабатывает запуск проекта через gradio_cli.py.
        """
        return f"{history}\n{run_project()}"
    
    # Связь кнопок с действиями
    execute_button.click(handle_command, inputs=[command_input, console_output], outputs=console_output)
    run_project_button.click(handle_run_project, inputs=[console_output], outputs=console_output)

    # Возвращаем элементы интерфейса
    return [console_output, command_input, execute_button, run_project_button]
