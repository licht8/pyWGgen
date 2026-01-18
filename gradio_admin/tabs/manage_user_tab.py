#!/usr/bin/env python3
# gradio_admin/tabs/manage_user_tab.py

import gradio as gr  # type: ignore
from gradio_admin.functions.delete_user import delete_user
from gradio_admin.functions.user_records import load_user_records
from gradio_admin.functions.block_user import block_user, unblock_user

# Import funkcji synchronizacji
from modules.sync import sync_users_from_config_paths

import os

WG_CONFIGS_PATH = "/root/pyWGgenerator/pyWGgen/user/data/wg_configs"

def get_user_config_path(username):
    """Pobiera ścieżkę do pliku konfiguracyjnego użytkownika."""
    possible_files = [
        f"{username}.conf",
        f"{username}_local.conf"
    ]
    for fname in possible_files:
        full_path = os.path.join(WG_CONFIGS_PATH, fname)
        if os.path.isfile(full_path):
            return full_path
    return None

def handle_download_config(selected_user):
    """Obsługuje pobieranie konfiguracji użytkownika."""
    if not selected_user or selected_user == "Wybierz użytkownika":
        return None, "Najpierw wybierz użytkownika."
    username = selected_user.split(" ")[0]
    config_path = get_user_config_path(username)
    if config_path:
        return config_path, f"Plik konfiguracji dla użytkownika {username} gotowy do pobrania."
    return None, f"Konfiguracja dla {username} nie znaleziona."

def manage_user_tab():
    """Tworzy zakładkę zarządzania użytkownikami (usuwanie, blokowanie, odblokowywanie)."""
    
    gr.Markdown("# 🛠️ Zarządzanie użytkownikami\n\nUsuwanie, blokowanie, odblokowywanie i pobieranie konfiguracji")

    def get_user_list():
        """Pobiera listę użytkowników z rekordów."""
        records = load_user_records()
        user_list = []
        for username, user_data in records.items():
            status = user_data.get("status", "nieznany")
            display_status = f"({status.capitalize()})" if status else ""
            user_list.append(f"{username} {display_status}".strip())
        return ["Wybierz użytkownika"] + user_list

    def refresh_user_list():
        return gr.update(choices=get_user_list(), value="Wybierz użytkownika"), "Lista użytkowników zaktualizowana."

    def handle_user_deletion(selected_user):
        """Obsługuje usuwanie użytkownika."""
        username = selected_user.split(" ")[0]
        success = delete_user(username)
        if success:
            return gr.update(choices=get_user_list(), value="Wybierz użytkownika"), f"Użytkownik '{username}' został usunięty."
        return gr.update(), f"Nie udało się usunąć użytkownika '{username}'."

    def handle_user_block(selected_user):
        """Obsługuje blokowanie użytkownika."""
        username = selected_user.split(" ")[0]
        success, message = block_user(username)
        return gr.update(choices=get_user_list(), value="Wybierz użytkownika"), message

    def handle_user_unblock(selected_user):
        """Obsługuje odblokowywanie użytkownika."""
        username = selected_user.split(" ")[0]
        success, message = unblock_user(username)
        return gr.update(choices=get_user_list(), value="Wybierz użytkownika"), message

    # Nowa funkcja dla przycisku "Synchronizuj"
    def handle_sync(config_dir_str, qr_dir_str):
        """Obsługuje synchronizację użytkowników."""
        success, log = sync_users_from_config_paths(config_dir_str, qr_dir_str)
        return log  # Zwraca logi synchronizacji

    # Wiersz z dropdownem i przyciskiem "Odśwież"
    with gr.Row():
        user_selector = gr.Dropdown(choices=get_user_list(), value="Wybierz użytkownika", interactive=True)
        refresh_button = gr.Button("Odśwież listę")

    # Wiersz z przyciskami Usuń, Blokuj, Odblokuj + Pobierz konfigurację
    with gr.Row():
        delete_button = gr.Button("Usuń użytkownika")
        block_button = gr.Button("Blokuj użytkownika")
        unblock_button = gr.Button("Odblokuj użytkownika")
        download_button = gr.Button("Pobierz konfigurację")

    # Pole do wyświetlania wyniku (usuwanie, blokowanie, odblokowywanie, pobieranie)
    with gr.Row():
        result_display = gr.Textbox(label="Wynik", value="", lines=2, interactive=False)

    # Wiersz z wynikiem pobierania
    with gr.Row():
        download_output = gr.File(label="Plik do pobrania")

    # ========= Nowe pola i przycisk "Synchronizuj" =========
    with gr.Row():
        config_dir_input = gr.Textbox(label="Ścieżka do katalogu konfiguracji", value="", lines=1)
        qr_dir_input = gr.Textbox(label="Ścieżka do katalogu kodów QR", value="", lines=1)
        sync_button = gr.Button("Synchronizuj")

    # Definiowanie zachowań przycisków
    refresh_button.click(
        fn=refresh_user_list,
        inputs=[],
        outputs=[user_selector, result_display]
    )
    delete_button.click(
        fn=handle_user_deletion,
        inputs=[user_selector],
        outputs=[user_selector, result_display]
    )
    block_button.click(
        fn=handle_user_block,
        inputs=[user_selector],
        outputs=[user_selector, result_display]
    )
    unblock_button.click(
        fn=handle_user_unblock,
        inputs=[user_selector],
        outputs=[user_selector, result_display]
    )
    sync_button.click(
        fn=handle_sync,
        inputs=[config_dir_input, qr_dir_input],
        outputs=[result_display]
    )
    download_button.click(
        fn=handle_download_config,
        inputs=[user_selector],
        outputs=[download_output, result_display]
    )
