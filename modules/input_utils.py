#!/usr/bin/env python3
# modules/input_utils.py
# Module for input with history support using readline.

import readline
import os

HISTORY_FILE = os.path.expanduser("~/.wg_input_history")
readline.set_history_length(50)

def setup_history():
    """
    Configures input history for readline.
    Loads an existing history or creates a new one.
    """
    try:
        readline.read_history_file(HISTORY_FILE)
    except FileNotFoundError:
        # If the history file does not exist, create an empty one
        open(HISTORY_FILE, "wb").close()

    # Set up automatic saving of history on exit
    import atexit
    atexit.register(readline.write_history_file, HISTORY_FILE)

def input_with_history(prompt):
    """
    Input with history support.

    :param prompt: Prompt text for the user.
    :return: User input string.
    """
    setup_history()
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print("\n ❌ Input canceled.")
        return ""
