#!/usr/bin/env python3
# gradio_admin/tabs/statistics_tab.py
# Zakładka "Statystyki" dla interfejsu Gradio projektu pyWGgen

import gradio as gr  # type: ignore
import pandas as pd  # type: ignore
import os
from pathlib import Path
from gradio_admin.functions.user_records import load_user_records
from gradio_admin.functions.format_helpers import format_time
from gradio_admin.functions.table_helpers import update_table
from gradio_admin.functions.format_helpers import format_user_info
from gradio_admin.functions.show_user_info import show_user_info
from modules.traffic_updater import update_traffic_data
from settings import USER_DB_PATH, QR_CODE_DIR

def statistics_tab():
    """Tworzy zakładkę statystyk dla użytkowników WireGuard."""
    
    gr.Markdown("# 🔍 Statystyki - Statystyka użytkowników\n\nPrzeglądanie statystyk, ruchu i informacji o użytkownikach")
    
    # Pobranie początkowych danych
    def get_initial_data():
        update_traffic_data(USER_DB_PATH)
        table = update_table(True)
        # ✅ Poprawione: zawsze zapewnij poprawne kolumny
        columns = ["👤 Użytkownik", "📊 Zużyto", "📦 Limit", "🌐 Adres IP", "⚡ Stan", "💳 Cena", "UID"]
        if table.empty:
            table = pd.DataFrame([], columns=columns)
        user_list = ["Wybierz użytkownika"] + table["👤 Użytkownik"].tolist()
        return table, user_list

    initial_table, initial_user_list = get_initial_data()
    
    # Funkcja do konwersji DataFrame na HTML
    def df_to_html(df):
        if df.empty:
            return "<p style='text-align: center; padding: 20px; color: #9ca3af;'>Brak dostępnych danych</p>"
        
        html = """
        <div style="width: 100%; overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; font-family: system-ui, -apple-system, sans-serif; font-size: 14px;">
                <thead>
                    <tr style="background-color: #0f0f11; color: #d1d5db;">
        """
        
        for idx, col in enumerate(df.columns):
            border_style = "border-bottom: 1px solid #3f3f46;"
            if idx < len(df.columns) - 1:
                border_style += " border-right: 1px solid #3f3f46;"
            html += f'<th style="padding: 12px 16px; text-align: left; font-weight: 600; {border_style}">{col}</th>'
        
        html += """
                    </tr>
                </thead>
                <tbody>
        """
        
        for row_idx, row in df.iterrows():
            # Naprzemienne kolory: #27272a i #2d2d30
            bg_color = "#27272a" if row_idx % 2 == 0 else "#2d2d30"
            html += f'<tr style="background-color: {bg_color}; color: #d1d5db;">'
            for col_idx, val in enumerate(row):
                border_style = ""
                if row_idx < len(df) - 1:
                    border_style += "border-bottom: 1px solid #3f3f46;"
                if col_idx < len(row) - 1:
                    border_style += " border-right: 1px solid #3f3f46;"
                html += f'<td style="padding: 10px 16px; {border_style}">{val}</td>'
            html += '</tr>'
        
        html += """
                </tbody>
            </table>
        </div>
        """
        return html

    # Checkbox "Pokaż zablokowanych" i przycisk Odśwież
    with gr.Row():
        show_inactive = gr.Checkbox(label="Pokaż zablokowanych", value=True, scale=1)
        refresh_button = gr.Button("Odśwież", scale=0, min_width=150)

    # Pole wyszukiwania
    search_input = gr.Textbox(label="Wyszukaj", placeholder="Wpisz tekst do filtrowania tabeli...", interactive=True)

    # Wybór użytkownika i wyświetlanie informacji oraz kodu QR
    with gr.Row(equal_height=True):
        with gr.Column(scale=3):
            user_selector = gr.Dropdown(
                label="Wybierz użytkownika",
                choices=initial_user_list,
                value="Wybierz użytkownika",
                interactive=True
            )
            user_info_display = gr.Textbox(
                label="Szczegóły użytkownika",
                value="",
                lines=10,
                interactive=False
            )
        with gr.Column(scale=1, min_width=200):
            qr_code_display = gr.Image(
                label="Kod QR użytkownika",
                type="filepath",
                interactive=False,
                height=200
            )

    # Tabela HTML zamiast Dataframe
    stats_table_html = gr.HTML(value=df_to_html(initial_table), elem_id="statistics_table")

    # Funkcja odświeżania tabeli i resetowania danych
    def refresh_table(show_inactive):
        update_traffic_data(USER_DB_PATH)
        table = update_table(show_inactive)
        columns = ["👤 Użytkownik", "📊 Zużyto", "📦 Limit", "🌐 Adres IP", "⚡ Stan", "💳 Cena", "UID"]
        
        if table.empty:
            table = pd.DataFrame([], columns=columns)
            print("[DEBUG] Tabela jest pusta po aktualizacji.")
        else:
            print(f"[DEBUG] Zaktualizowana tabela:\n{table}")
        
        user_list = ["Wybierz użytkownika"] + table["👤 Użytkownik"].tolist()
        print(f"[DEBUG] Lista użytkowników: {user_list}")
        return "", df_to_html(table), gr.update(choices=user_list, value="Wybierz użytkownika"), "", None

    refresh_button.click(
        fn=refresh_table,
        inputs=[show_inactive],
        outputs=[search_input, stats_table_html, user_selector, user_info_display, qr_code_display]
    )

    def search_table(query):
        """Filtrowanie tabeli według zapytania wyszukiwania."""
        table = update_table(True)
        columns = ["👤 Użytkownik", "📊 Zużyto", "📦 Limit", "🌐 Adres IP", "⚡ Stan", "💳 Cena", "UID"]
        if table.empty:
            table = pd.DataFrame([], columns=columns)
        
        if query:
            filtered_table = table.loc[
                table.apply(lambda row: query.lower() in " ".join(map(str, row)).lower(), axis=1)
            ]
            print(f"[DEBUG] Filtrowana tabela:\n{filtered_table}")
            return df_to_html(filtered_table)
        return df_to_html(table)

    search_input.change(
        fn=search_table,
        inputs=[search_input],
        outputs=[stats_table_html]
    )

    def find_qr_code(username):
        """Znajduje plik kodu QR dla użytkownika."""
        qr_code_file = Path(QR_CODE_DIR) / f"{username}.png"
        if qr_code_file.exists():
            return str(qr_code_file)
        return None

    def display_user_info(selected_user):
        """Wyświetla informacje o wybranym użytkowniku."""
        if isinstance(selected_user, list):
            if len(selected_user) > 0:
                selected_user = selected_user[0]
            else:
                selected_user = "Wybierz użytkownika"

        if not selected_user or selected_user == "Wybierz użytkownika":
            return "", None

        user_info = show_user_info(selected_user)
        qr_code_path = find_qr_code(selected_user)
        print(f"[DEBUG] Informacje o użytkowniku:\n{user_info}")
        print(f"[DEBUG] Ścieżka kodu QR dla {selected_user}: {qr_code_path}")
        return user_info, qr_code_path

    user_selector.change(
        fn=display_user_info,
        inputs=[user_selector],
        outputs=[user_info_display, qr_code_display]
    )
