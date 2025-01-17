#!/usr/bin/env python3
# test_llm.py
# ==================================================
# Test script for verifying interaction with LLM.
# Version: 1.5 (2024-12-21)
# ==================================================
# Description:
# This script tests the transmission of a system prompt and user query to the model
# to avoid duplication in responses.
# ==================================================

import requests
import logging

# API Configuration
LLM_API_URL = "http://10.67.67.2:11434/api/generate"
MODEL_NAME = "llama3:latest"

# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def test_query_llm():
    """Test query to LLM with a system prompt."""
    try:
        # System and user prompts
        system_prompt = "You are a professional WireGuard administrator. Your name is Pulka. Start every response with 'Hi, I am Pulka!'"
        user_prompt = "Tell me a bit about yourself."

        # Full prompt
        prompt = f"{system_prompt}\n\n{user_prompt}"

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }

        logger.info(f"Sending request to LLM: {LLM_API_URL}")
        response = requests.post(LLM_API_URL, json=payload)
        response.raise_for_status()

        result = response.json()
        return result.get("response", "Error: No response")

    except requests.HTTPError as http_err:
        logger.error(f"HTTP error while communicating with LLM: {http_err}")
        return f"HTTP Error: {http_err}"
    except Exception as e:
        logger.error(f"Error while communicating with LLM: {e}")
        return f"Error: {e}"

if __name__ == "__main__":
    response = test_query_llm()
    print("\nLLM Response:")
    print(response)
