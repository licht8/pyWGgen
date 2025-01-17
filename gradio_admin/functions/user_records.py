#!/usr/bin/env python3
# gradio_admin/functions/user_records.py
# Utilities for working with user data in the wg_qr_generator project

import json
import os

USER_RECORDS_PATH = os.path.join(os.path.dirname(__file__), "../../user/data/user_records.json")

def load_user_records():
    """Loads user data from the user_records.json file."""
    try:
        with open(USER_RECORDS_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[DEBUG] user_records.json not found!")
        return {}
    except json.JSONDecodeError as e:
        print(f"[DEBUG] JSON decode error in user_records.json: {e}")
        return {}
