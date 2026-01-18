#!/usr/bin/env python3
# gradio_admin/functions/user_records.py
# Narzędzia do pracy z danymi użytkowników w projekcie wg_qr_generator

import json
import os

USER_RECORDS_PATH = os.path.join(os.path.dirname(__file__), "../../user/data/user_records.json")

def load_user_records():
    """Wczytuje dane użytkowników z pliku user_records.json."""
    try:
        with open(USER_RECORDS_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[DEBUG] Plik user_records.json nie znaleziony!")
        return {}
    except json.JSONDecodeError as e:
        print(f"[DEBUG] Błąd dekodowania JSON w user_records.json: {e}")
        return {}
