"""Asystent AI dla diagnostyki VPN pyWGgen."""

from .data_collector import collect_all_data
from .ai_chat import interactive_mode, ask_question
from .ai_analyzer import analyze_with_ai
from .ai_report import generate_report, show_report_menu
from .utils import save_json_log, check_ollama

__all__ = [
    'collect_all_data',
    'interactive_mode',
    'ask_question',
    'analyze_with_ai',
    'generate_report',
    'show_report_menu',
    'save_json_log',
    'check_ollama'
]
