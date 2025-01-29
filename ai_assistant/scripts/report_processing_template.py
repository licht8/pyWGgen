#!/usr/bin/env python3
# report_processing_template.py
# ==================================================
# Script for processing data and sending requests to the LLM model.
# Version: 1.1
# ==================================================

import sys
import requests
import logging
from pathlib import Path
from datetime import datetime

# === Path Configuration ===
# Add the project root directory to sys.path
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
PROMPT_POSITION = "before"  # System prompt position: "before" or "after"

# File Paths
DATA_FILE = BASE_DIR / "ai_assistant/inputs/test_data.txt"  # Path to the data file
PROMPT_FILE = BASE_DIR / "ai_assistant/prompts/test_prompt.txt"  # Path to the prompt file

# Logging configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(BASE_DIR / f'logs/report_processing_{datetime.now().strftime("%Y%m%d")}.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.propagate = False

# === Functions ===
def read_file(filepath):
    """Reads the contents of a file."""
    try:
        with open(filepath, "r") as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"File {filepath} not found.")
        sys.exit(1)

def query_llm(api_url, data, model):
    """Sends a request to the LLM and returns the response."""
    payload = {
        "model": model,
        "prompt": data,
        "stream": False
    }
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json().get("response", "<Empty response from model>")
    except requests.RequestException as e:
        logger.error(f"Error querying LLM: {e}")
        return None

def process_report():
    """Processes data and sends a request to the LLM."""
    logger.info("\n=== Starting Report Processing ===")

    # Read data and prompt
    data = read_file(DATA_FILE)
    prompt = read_file(PROMPT_FILE)

    # Format data for sending
    if PROMPT_POSITION == "before":
        combined_data = f"{prompt}\n\n{data}"
    else:
        combined_data = f"{data}\n\n{prompt}"

    logger.info("Sending data to LLM...")
    response = query_llm(LLM_API_URL, combined_data, MODEL)

    if response:
        logger.info(f"Response from LLM:\n{response}")
    else:
        logger.error("No response from LLM.")

# === Entry Point ===
if __name__ == "__main__":
    process_report()
