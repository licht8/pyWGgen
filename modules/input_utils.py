#!/usr/bin/env python3
# modules/input_utils.py
# Модуль для ввода с поддержкой истории через readline.

import readline
import os

HISTORY_FILE = os.path.expanduser("~/.wg_input_history")

def setup_history():
    """
    Настраивает историю ввода для readline.
    Загружает существующую историю или создает новую.
    """
    try:
        readline.read_history_file(HISTORY_FILE)
    except FileNotFoundError:
        # Если файла истории нет, создаем пустой
        open(HISTORY_FILE, "wb").close()

    # Устанавливаем автоматическое сохранение истории при завершении
    import atexit
    atexit.register(readline.write_history_file, HISTORY_FILE)

def input_with_history(prompt):
    """
    Ввод с поддержкой истории.
    
    :param prompt: Текст подсказки для ввода.
    :return: Строка ввода пользователя.
    """
    setup_history()
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print("\n ❌ Ввод отменен.")
        return ""
