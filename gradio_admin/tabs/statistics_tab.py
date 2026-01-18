#!/usr/bin/env python3
# gradio_admin/tabs/statistics_tab.py
# Zakładka Statystyki - pełna wersja z poprawkami

import gradio as gr
import pandas as pd
from functions.table_helpers import update_table
from functions.user_helpers import update_traffic_data, df_to_html
from settings import USER_DB_PATH

def get_initial_data():
    """Pobiera początkowe dane dla zakładki Statystyki."""
    update_traffic_data(USER_DB_PATH)
    table = update_table(True)
    
    # Zawsze zapewnij poprawne kolumny
    columns = ["👤 Użytkownik", "📊 Zużyto", "📦 Limit", "🌐 Adres IP", "⚡ Stan", "💳 Cena", "UID"]
    
    if table.empty:
        print("[DEBUG] Tabela początkowa jest pusta.")
        table = pd.DataFrame([], columns=columns)
        user_list = ["Wybierz użytkownika"]
    else:
        print(f"[DEBUG] Początkowa tabela:\n{table}")
        user_list = ["Wybierz użytkownika"] + table["👤 Użytkownik"].tolist()
    
    return table, user_list

def refresh_table(show_inactive):
    """Odświeża tabelę użytkowników z aktualnymi danymi."""
    update_traffic_data(USER_DB_PATH)
    table = update_table(show_inactive)
    
    columns = ["👤 Użytkownik", "📊 Zużyto", "📦 Limit", "🌐 Adres IP", "⚡ Stan", "💳 Cena", "UID"]
    
    if table.empty:
        print("[DEBUG] Tabela jest pusta po aktualizacji.")
        empty_table = pd.DataFrame([], columns=columns)
        return (
            "", 
            df_to_html(empty_table), 
            gr.update(choices=["Wybierz użytkownika"], value="Wybierz użytkownika"), 
            "", 
            None
        )
    
    print(f"[DEBUG] Zaktualizowana tabela:\n{table}")
    user_list = ["Wybierz użytkownika"] + table["👤 Użytkownik"].tolist()
    print(f"[DEBUG] Lista użytkowników: {user_list}")
    
    return (
        "", 
        df_to_html(table), 
        gr.update(choices=user_list, value="Wybierz użytkownika"), 
        "", 
        None
    )

def get_user_stats(selected_user):
    """Pobiera szczegółowe statystyki wybranego użytkownika."""
    if selected_user == "Wybierz użytkownika" or not selected_user:
        return "", "", "", None
    
    print(f"[DEBUG] Wybrano użytkownika: {selected_user}")
    
    # Tutaj możesz dodać logikę pobierania szczegółowych danych użytkownika
    # Na razie zwracamy placeholder
    stats_info = f"""
    📊 Szczegóły użytkownika: **{selected_user}**
    
    🔄 Status: aktywny
    📈 Zużycie danych: 0.00 MiB
    ⏱️ Ostatnie logowanie: -
    🌐 IP: -
    💳 Subskrypcja: 0.00 PLN/miesiąc
    """
    
    return (
        f"Wybrano: {selected_user}",
        stats_info,
        "", 
        None
    )

def create_statistics_tab():
    """Tworzy zakładkę Statystyki z pełnym interfejsem."""
    with gr.TabItem("📊 Statystyka", id="statistics"):
        gr.Markdown("# 📊 Statystyka użytkowników WireGuard")
        
        with gr.Row():
            with gr.Column(scale=2):
                # Checkbox do pokazywania nieaktywnych
                show_inactive_cb = gr.Checkbox(
                    label="Pokaż nieaktywnych użytkowników", 
                    value=False
                )
                
                # Przycisk odświeżania
                refresh_btn = gr.Button("🔄 Odśwież dane", variant="primary")
                
                gr.Markdown("### 📋 Lista wszystkich użytkowników")
                
                # Tabela główny widok
                table_output = gr.HTML()
                
            with gr.Column(scale=1):
                gr.Markdown("### 👤 Wybierz użytkownika")
                
                # Dropdown wyboru użytkownika
                user_dropdown = gr.Dropdown(
                    label="Użytkownicy",
                    choices=["Wybierz użytkownika"],
                    value="Wybierz użytkownika"
                )
                
                # Szczegóły użytkownika
                selected_user_info = gr.Textbox(
                    label="Wybrany użytkownik", 
                    interactive=False
                )
                
                user_details = gr.Markdown()
        
        # Ładowanie początkowych danych
        table_data, user_choices = get_initial_data()
        user_dropdown.change(
            get_user_stats,
            inputs=user_dropdown,
            outputs=[selected_user_info, user_details]
        )
        
        # Odświeżanie tabeli
        refresh_btn.click(
            refresh_table,
            inputs=show_inactive_cb,
            outputs=[table_output, user_dropdown]
        ).then(
            get_user_stats,
            inputs=user_dropdown,
            outputs=[selected_user_info, user_details]
        )
        
        # show_inactive_cb.change(
        #     refresh_table,
        #     inputs=show_inactive_cb,
        #     outputs=[table_output, user_dropdown]
        # )
        
        # Inicjalizacja
        return (
            table_output,
            user_dropdown,
            selected_user_info,
            user_details,
            refresh_btn,
            show_inactive_cb
        )

# Uruchomienie zakładki (jeśli plik jest uruchamiany bezpośrednio)
if __name__ == "__main__":
    demo = gr.Blocks()
    with demo:
        create_statistics_tab()
    demo.launch()
