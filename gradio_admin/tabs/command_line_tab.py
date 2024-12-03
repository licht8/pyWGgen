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
    console_history = []

    def run_command(command, current_history):
        """
        Выполняет команду в терминале и возвращает результат.
        """
        global console_history
        try:
            result = subprocess.run(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            console_history = current_history + [f"$ {command}", result.stdout.strip() or result.stderr.strip()]
        except Exception as e:
            console_history.append(f"Ошибка: {e}")
        return "\n".join(console_history), console_history

    def clear_console():
        """
        Очищает историю консоли.
        """
        nonlocal console_history
        console_history = []
        return "", console_history

    execute_button.click(
        run_command,
        inputs=[command_input, output_console],
        outputs=[output_console]
    )

    clear_button.click(
        clear_console,
        inputs=[],
        outputs=[output_console]
    )

    return [command_input, execute_button, output_console, clear_button]
