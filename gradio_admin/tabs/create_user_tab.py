#!/usr/bin/env python3
# gradio_admin/tabs/create_user_tab.py
# Zakładka do tworzenia użytkowników

import gradio as gr
from gradio_admin.functions.create_user import create_user

def create_user_tab():
    """
    Zakładka do tworzenia użytkowników WireGuard.
    """
    gr.Markdown("# 🌱 Tworzenie użytkownika\n\nUtwórz nowego użytkownika WireGuard z konfiguracją i kodem QR")
    
    username_input = gr.Textbox(label="Nazwa użytkownika", placeholder="Wpisz nazwę użytkownika...")
    email_input = gr.Textbox(label="Email (opcjonalnie)", placeholder="Wpisz email...")
    telegram_input = gr.Textbox(label="ID Telegram (opcjonalnie)", placeholder="Wpisz ID Telegram...")
    create_button = gr.Button("Utwórz użytkownika")
    output_message = gr.Textbox(label="Wynik", interactive=False)
    qr_code_display = gr.Image(label="Kod QR", visible=False)

    def handle_create_user(username, email, telegram_id):
        result, qr_code_path = create_user(username, email, telegram_id)
        
        # Rozdziel komunikaty sukcesu i błędu
        if result.startswith("✅"):
            return result, gr.update(visible=True, value=qr_code_path) if qr_code_path else gr.update(visible=False)
        else:
            return result, gr.update(visible=False)

    create_button.click(
        handle_create_user,
        inputs=[username_input, email_input, telegram_input],
        outputs=[output_message, qr_code_display]
    )
    
    return [username_input, email_input, telegram_input, create_button, output_message, qr_code_display]
