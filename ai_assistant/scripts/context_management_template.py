#!/usr/bin/env python3
# ai_assistant/scripts/chat_with_context.py
# ==================================================
# Script for interacting with an LLM model while preserving 
# the dialogue context.
# Version: 1.5
# ==================================================

import requests
import sys
from pathlib import Path
from datetime import datetime
import logging
import readline  # For console navigation and editing support

# === Path Configuration ===
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import project settings
try:
    from settings import BASE_DIR, LLM_API_URL
except ImportError as e:
    print(f"Error importing settings: {e}")
    sys.exit(1)

# === Settings ===
MODEL = "qwen2:7b"  # Model name for processing
HISTORY_FILE = BASE_DIR / "ai_assistant/context/context_history.txt"
MAX_HISTORY_LENGTH = 50  # Maximum number of messages in history

# Chat colors
class Colors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    RED = "\033[91m"
    RESET = "\033[0m"

# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(BASE_DIR / f'logs/chat_with_context_{datetime.now().strftime("%Y%m%d")}.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.propagate = False

# === Global Variable for Storing History ===
dialog_history = []

# === Functions ===
def save_dialog_history():
    """Saves the dialogue history to a text file."""
    try:
        with open(HISTORY_FILE, "w") as file:
            file.write("\n".join(dialog_history))
        logger.info(f"Dialogue history saved in {HISTORY_FILE}")
    except Exception as e:
        logger.error(f"Error saving dialogue history: {e}")

def load_dialog_history():
    """Loads the dialogue history from a text file."""
    global dialog_history
    if HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 0:
        try:
            with open(HISTORY_FILE, "r") as file:
                dialog_history = file.read().splitlines()
            logger.info(f"Dialogue history loaded from {HISTORY_FILE}")
        except Exception as e:
            logger.error(f"Error loading dialogue history: {e}")
            dialog_history = []
    else:
        dialog_history = []

def query_llm_with_context(user_input):
    """Sends a request to the LLM while considering dialogue history."""
    global dialog_history

    # Add user message to history
    dialog_history.append(f"You: {user_input}")
    if len(dialog_history) > MAX_HISTORY_LENGTH * 2:  # Multiply by 2 (one message from user and one from assistant)
        dialog_history = dialog_history[-MAX_HISTORY_LENGTH * 2:]

    payload = {
        "model": MODEL,
        "prompt": "\n".join(dialog_history),
        "stream": False
    }

    try:
        response = requests.post(LLM_API_URL, json=payload)
        response.raise_for_status()

        # Get response from the model
        model_response = response.json().get("response", "<No response>")
        dialog_history.append(f"Assistant: {model_response}")

        # Save history
        save_dialog_history()

        return model_response
    except requests.RequestException as e:
        logger.error(f"Error requesting the model: {e}")
        return None

# === Main Process ===
if __name__ == "__main__":
    load_dialog_history()

    print("Welcome to the LLM chat! Type 'exit' to quit.")

    try:
        while True:
            user_input = input(f"{Colors.BLUE}You: {Colors.WHITE}")
            if user_input.lower() == "exit":
                print(f"{Colors.GREEN}Chat ended. History saved.{Colors.RESET}")
                break

            response = query_llm_with_context(user_input)
            if response:
                print(f"{Colors.GREEN}Assistant:{Colors.GRAY} {response}{Colors.RESET}")
            else:
                print(f"{Colors.GREEN}Assistant:{Colors.GRAY} Error: no response from the model.{Colors.RESET}")
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Chat interrupted by user. History saved.{Colors.RESET}")
        save_dialog_history()
        sys.exit(0)
