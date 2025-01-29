#!/usr/bin/env python3
# ai_assistant/scripts/execute_llm_reports.py
# ==================================================
# Script for sequentially generating reports and 
# querying the LLM model.
# Version: 1.4
# ==================================================

import subprocess
import sys
import requests
import logging
from pathlib import Path
from datetime import datetime

# Add the project's root path to sys.path for importing settings
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
    PROJECT_ROOT = SCRIPT_DIR.parent.parent
    sys.path.append(str(PROJECT_ROOT))
    from settings import BASE_DIR, LLM_API_URL
except ImportError as e:
    print(f"Error importing settings: {e}")
    sys.exit(1)

# === Settings ===

#MODEL = "llama3:latest"  # Model name for processing
#MODEL = "gemma:7b"  # Model name for processing
#MODEL = "dolphin-mixtral:latest"  # Model name for processing
MODEL = "qwen2:7b"  # Model name for processing
USER_REPORT_SCRIPT = BASE_DIR / "ai_assistant/scripts/generate_user_report.py"
SYSTEM_REPORT_SCRIPT = BASE_DIR / "ai_assistant/scripts/generate_system_report.py"
USER_REPORT_FILE = BASE_DIR / "ai_assistant/outputs/user_report.txt"
SYSTEM_REPORT_FILE = BASE_DIR / "ai_assistant/outputs/system_report.txt"
USER_PROMPT_FILE = BASE_DIR / "ai_assistant/prompts/generate_user_report.txt"
SYSTEM_PROMPT_FILE = BASE_DIR / "ai_assistant/prompts/generate_system_report.txt"

# Logging configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(BASE_DIR / f'logs/execute_reports_{datetime.now().strftime("%Y%m%d")}.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.propagate = False

# === Functions ===
def run_script(script_path):
    """Executes the specified script."""
    try:
        result = subprocess.run(["python3", script_path], check=True, text=True)
        logger.info(f"{script_path} executed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing {script_path}: {e}")
        sys.exit(1)

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

def process_report(report_file, prompt_file, model):
    """Processes a report and sends a request to the LLM."""
    report_data = read_file(report_file)
    prompt_data = read_file(prompt_file)

    # System prompt is added after the data
    combined_data = f"{report_data}\n\n{prompt_data}"

    logger.info(f"\nSending data to LLM for {report_file}...")
    response = query_llm(LLM_API_URL, combined_data, model)

    if response:
        logger.info(f"Response from LLM for {report_file.name}:\n{response}")
    else:
        logger.error(f"No response from LLM for {report_file.name}.")

# === Main Process ===
if __name__ == "__main__":
    logger.info("Generating reports...")

    # Generate user report
    run_script(USER_REPORT_SCRIPT)

    # Generate system report
    run_script(SYSTEM_REPORT_SCRIPT)

    logger.info("\nLoading reports and prompts...")

    # Process user report (system prompt at the end)
    #process_report(USER_REPORT_FILE, USER_PROMPT_FILE, MODEL)
    # Process user report (system prompt at the beginning)
    process_report(USER_PROMPT_FILE, USER_REPORT_FILE, MODEL)

    # Process system report (system prompt at the end)
    process_report(SYSTEM_REPORT_FILE, SYSTEM_PROMPT_FILE, MODEL)
    # Process system report (system prompt at the beginning)
    #process_report(SYSTEM_PROMPT_FILE, SYSTEM_REPORT_FILE, MODEL)
