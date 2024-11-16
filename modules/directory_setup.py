import os
import json
import settings

def setup_directories():
    directories = [
        settings.WG_CONFIG_DIR,
        settings.QR_CODE_DIR,
        settings.STALE_CONFIG_DIR,
        os.path.dirname(settings.USER_DB_PATH)
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    if not os.path.exists(settings.USER_DB_PATH):
        with open(settings.USER_DB_PATH, 'w') as file:
            json.dump({}, file, indent=4)
