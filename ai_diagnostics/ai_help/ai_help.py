#!/usr/bin/env python3
# ai_diagnostics/ai_help/ai_help.py
# Help system for the pyWGgen project.
# Version: 2.6
# Updated: 2024-12-04
# New:
# - Input history support with arrow key navigation.

import json
import sys
import logging
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

# Setting project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODULES_DIR = PROJECT_ROOT / "ai_diagnostics" / "modules"
HELP_DIR = PROJECT_ROOT / "ai_diagnostics" / "ai_help"
SETTINGS_FILE = PROJECT_ROOT / "settings.py"

sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(MODULES_DIR))

# Logging setup
LOG_FILE = PROJECT_ROOT / "user/data/logs/app.log"
LOG_LEVEL = logging.DEBUG  # Logging levels: DEBUG, INFO, WARNING, ERROR

logging.basicConfig(
    filename=LOG_FILE,
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Imports
try:
    from pause_rules import apply_pause, get_pause_rules  # Fixed path to pause_rules
    from ai_diagnostics.ai_diagnostics import display_message_slowly
    from modules.input_utils import input_with_history  # Correct import for input_utils
except ImportError as e:
    logging.error(f"❌ Module import error: {e}")
    print(f"❌ Module import error: {e}")
    sys.exit(1)

# Text formatting configuration
LINE_WIDTH = {
    "menu": 60,
    "details": 70
}

def wrap_text(text, width, indent=4):
    """Formats text to a specified width with indentation."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 > width:
            lines.append(" " * indent + current_line)
            current_line = word
        else:
            current_line += ("" if current_line == "" else " ") + word

    if current_line:
        lines.append(" " * indent + current_line)

    return "\n".join(lines)

def preserve_json_formatting(text, indent=4):
    """Formats text while preserving original JSON indentation and line breaks."""
    lines = []
    for line in text.split("\n"):
        if line.strip():  # Add indentation for non-empty lines
            lines.append(" " * indent + line)
        else:  # Preserve empty lines without indentation
            lines.append("")
    return "\n".join(lines)

def load_settings():
    """Loads settings from settings.py."""
    settings = {}
    if SETTINGS_FILE.exists():
        spec = spec_from_file_location("settings", SETTINGS_FILE)
        settings_module = module_from_spec(spec)
        spec.loader.exec_module(settings_module)
        settings = {key: getattr(settings_module, key) for key in dir(settings_module) if not key.startswith("__")}
    return settings

SETTINGS = load_settings()

def replace_variables(text):
    """Replaces placeholders like {VARIABLE} with values from SETTINGS."""
    for key, value in SETTINGS.items():
        text = text.replace(f"{{{key}}}", str(value))
    return text

def load_help_files():
    """Loads all JSON help files from HELP_DIR."""
    logging.debug(f"Checking help directory: {HELP_DIR}")
    help_data = {}
    for json_file in HELP_DIR.rglob("*.json"):
        try:
            logging.debug(f"Processing help file: {json_file}")
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                for key, section in data.items():
                    if "title" not in section or ("short" not in section and "long" not in section):
                        logging.warning(f"⚠️ Issue in section '{key}': missing 'title', 'short', or 'long' key.")
                help_data.update(data)
        except Exception as e:
            logging.error(f"⚠️ Error loading file {json_file}: {e}")
    return help_data

def save_help_section(section):
    """Saves a help section to a file."""
    filename = f"{section['title'].strip()}.txt".replace(" ", "_")
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"{section['title']}\n")
        file.write("=" * len(section['title']) + "\n")
        file.write(wrap_text(section.get('long', "Detailed information not available."), LINE_WIDTH["details"]) + "\n")
    print(f"\n   📁  Section saved to file: {filename}\n")

def display_help_menu(help_data):
    """Displays the main menu of the help system."""
    print("\n   📖  Help System")
    print("   ======================")
    for idx, section in enumerate(help_data.values(), start=1):
        print(f"   {idx}. {section['title']}")
        print(wrap_text(section['short'], LINE_WIDTH["menu"], indent=6) + "\n")
    print("   0. Exit Help\n")

def display_detailed_help(section):
    """Displays detailed information for a selected section."""
    if 'long' not in section:
        logging.warning(f"⚠️ Issue in section '{section['title']}': missing 'long' key.")
        print(f"⚠️ Issue in section '{section['title']}': missing 'long' key.")
        return

    # Title
    print(f"\n   {section['title']}\n")
    print(f"   {'=' * (len(section['title'].strip()) + 4)}\n")

    # Replace variables and preserve formatting
    formatted_text = replace_variables(section.get('long', "Detailed information not available."))
    formatted_text = preserve_json_formatting(formatted_text)

    # Display text
    display_message_slowly(formatted_text)

    # Save section
    print("\n   🔹 Would you like to save this section? (y/n): ", end="")
    user_input = input_with_history("").strip().lower()
    if user_input in {"y", "yes"}:
        save_help_section(section)
    elif user_input in {"0", "q"}:
        print("\n   📖  Returning to the main menu.")

def interactive_help():
    """Main loop for interacting with the help system."""
    help_data = load_help_files()
    if not help_data:
        print("   ❌  Help information is unavailable.")
        return

    while True:
        display_help_menu(help_data)
        user_input = input_with_history("   Select a section number or enter a keyword: ").strip().lower()

        if user_input in {"0", "q", "exit"}:
            print("\n   📖  Exiting the help system.")
            break

        if user_input.isdigit():  # Check if input is a number
            index = int(user_input)
            if 1 <= index <= len(help_data):  # If it's a valid section number
                section = list(help_data.values())[index - 1]
                display_detailed_help(section)
                continue
        else:  # Search by text
            matches = [
                section for section in help_data.values()
                if user_input in section['title'].lower() or
                user_input in section['short'].lower() or
                user_input in section.get('long', "").lower()
            ]

            if len(matches) == 1:
                display_detailed_help(matches[0])
            elif len(matches) > 1:
                display_help_menu({"matches": matches})
            else:
                print("\n   ❌  No matches found. Try another query.\n")

if __name__ == "__main__":
    interactive_help()
