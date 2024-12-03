#!/usr/bin/env python3
# gradio_admin/tabs/command_line_tab.py
# Вкладка для работы с командной строкой

import gradio as gr
import subprocess

def command_line_tab():
    """
    Вкладка для эмуляции командной строки.
    """
    command_input = gr.Textbox(label="Введите команду", placeholder="Например: ls или dir")
    execute_button = gr.Button("Выполнить")
    output_console = gr.Textbox(label="Вывод консоли", interactive=False, lines=20)
    clear_button = gr.Button("Очистить консоль")
    console_history = []  # Локальная переменная для хранения истории

    def run_command(command):
        """
        Выполняет команду в терминале и возвращает результат.
        """
        nonlocal console_history  # Указываем, что работаем с локальной переменной
        try:
            result = subprocess.run(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            if stdout:
                console_history.append(f"$ {command}\n{stdout}")
            if stderr:
                console_history.append(f"$ {command}\nОшибка: {stderr}")
        except Exception as e:
            console_history.append(f"Ошибка выполнения команды: {e}")
        return "\n".join(console_history)

    def clear_console():
        """
        Очищает историю консоли.
        """
        nonlocal console_history
        console_history = []
        return ""

    # Привязка функций к элементам интерфейса
    execute_button.click(
        run_command,
        inputs=[command_input],
        outputs=[output_console]
    )

    clear_button.click(
        clear_console,
        inputs=[],
        outputs=[output_console]
    )

    return [command_input, execute_button, output_console, clear_button]
