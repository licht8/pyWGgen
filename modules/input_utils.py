#!/usr/bin/env python3
# modules/input_utils.py
# Moduł do wprowadzania danych z obsługą historii za pomocą readline.

import readline
import os

HISTORY_FILE = os.path.expanduser("~/.wg_input_history")
readline.set_history_length(50)

def setup_history():
    """
    Konfiguruje historię wprowadzania dla readline.
    Wczytuje istniejącą historię lub tworzy nową.
    """
    try:
        readline.read_history_file(HISTORY_FILE)
    except FileNotFoundError:
        # Jeśli plik historii nie istnieje, utwórz pusty
        open(HISTORY_FILE, "wb").close()

    # Ustaw automatyczne zapisywanie historii przy wyjściu
    import atexit
    atexit.register(readline.write_history_file, HISTORY_FILE)

def input_with_history(prompt):
    """
    Wprowadzanie z obsługą historii.

    :param prompt: Tekst podpowiedzi dla użytkownika.
    :return: Wprowadzony przez użytkownika ciąg znaków.
    """
    setup_history()
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print("\n ❌ Wprowadzanie anulowane.")
        return ""
