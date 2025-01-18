#!/usr/bin/env python3
# ai_diagnostics/modules/pause_rules.py
# Module for defining pause rules and expressive text reading.
# Version: 1.0
# Updated: 2024-11-29

import time
import random

def get_pause_rules():
    """
    Returns a list of rules for pauses based on various punctuation marks and contexts.
    """
    return [
        {
            "trigger": ".",  # Period
            "pause_range": (0.4, 0.8),  # Pause between 0.4 and 0.8 seconds
            "emotion": "neutral sentence ending"
        },
        {
            "trigger": ",",  # Comma
            "pause_range": (0.2, 0.4),  # Short pause
            "emotion": "list or light pause"
        },
        {
            "trigger": "!",  # Exclamation mark
            "pause_range": (0.5, 1.0),  # Longer pause
            "emotion": "excitement, surprise, or strong emotion"
        },
        {
            "trigger": "?",  # Question mark
            "pause_range": (0.6, 1.2),  # Thoughtful pause
            "emotion": "question, anticipation of an answer"
        },
        {
            "trigger": ":",  # Colon
            "pause_range": (0.3, 0.7),  # Slight pause
            "emotion": "anticipation of important information"
        },
        {
            "trigger": ";",  # Semicolon
            "pause_range": (0.3, 0.6),  # Short pause
            "emotion": "additional clarification"
        },
        {
            "trigger": "—",  # Dash
            "pause_range": (0.3, 0.5),  # Light pause
            "emotion": "sharp shift in thought"
        },
        {
            "trigger": "\n",  # Line break
            "pause_range": (0.6, 1.0),  # Moderate pause
            "emotion": "start of a new line or paragraph"
        }
    ]


def apply_pause(char, rules):
    """
    Applies a pause based on the character and defined rules.

    Args:
        char (str): The character after which to pause.
        rules (list): List of pause rules.

    Returns:
        None
    """
    for rule in rules:
        if char == rule["trigger"]:
            pause = random.uniform(*rule["pause_range"])
            time.sleep(pause)
            break
