# gradio_admin/tabs/statistics_tab.py
# "Statistics" tab for the Gradio interface of the pyWGgen project

import gradio as gr  # type: ignore
import pandas as pd  # type: ignore
from gradio_admin.functions.user_records import load_user_records
from gradio_admin.functions.format_helpers import format_time
from gradio_admin.functions.table_helpers import update_table
from gradio_admin.functions.format_helpers import format_user_info
from gradio_admin.functions.user_records import load_user_records
from gradio_admin.functions.show_user_info import show_user_info
from modules.traffic_updater import update_traffic_data
from settings import USER_DB_PATH
from settings import QR_CODE_DIR

def statistics_tab():
    """Creates a statistics tab for WireGuard users."""
    
    gr.Markdown("# 🔍 Statistics - Статистика пользователей\n\nПросмотр статистики, трафика и информации о пользователях")
    
    # Fetch initial data
    def get_initial_data():
        update_traffic_data(USER_DB_PATH)
        table = update_table(True)
        user_list = ["Select a user"] + table["👤 User"].tolist() if not table.empty else ["Select a user"]
        return table, user_list

    initial_table, initial_user_list = get_initial_data()
    
    # Функция для конвертации DataFrame в HTML
    def df_to_html(df):
        if df.empty:
            return "<p style='text-align: center; padding: 20px; color: #9ca3af;'>No data available</p>"
        
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
            # Чередование: #27272a и немного светлее (#2d2d30)
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

    # Show inactive checkbox and Refresh button
    with gr.Row():
        show_inactive = gr.Checkbox(label="Show blocked", value=True, scale=1)
        refresh_button = gr.Button("Refresh", scale=0, min_width=150)

    # Search field
    search_input = gr.Textbox(label="Search", placeholder="Enter text to filter table...", interactive=True)

    # User selection and display of information and QR code
    with gr.Row(equal_height=True):
        with gr.Column(scale=3):
            user_selector = gr.Dropdown(
                label="Select User",
                choices=initial_user_list,
                value="Select a user",
                interactive=True
            )
            user_info_display = gr.Textbox(
                label="User Details",
                value="",
                lines=10,
                interactive=False
            )
        with gr.Column(scale=1, min_width=200):
            qr_code_display = gr.Image(
                label="User QR Code",
                type="filepath",
                interactive=False,
                height=200
            )

    # HTML таблица вместо Dataframe
    stats_table_html = gr.HTML(value=df_to_html(initial_table), elem_id="statistics_table")

    # Function to refresh the table and reset data
    def refresh_table(show_inactive):
        update_traffic_data(USER_DB_PATH)
        table = update_table(show_inactive)
        if table.empty:
            print("[DEBUG] Table is empty after update.")
        else:
            print(f"[DEBUG] Updated table:\n{table}")
        user_list = ["Select a user"] + table["👤 User"].tolist() if not table.empty else ["Select a user"]
        print(f"[DEBUG] User list: {user_list}")
        return "", df_to_html(table), gr.update(choices=user_list, value="Select a user"), "", None

    refresh_button.click(
        fn=refresh_table,
        inputs=[show_inactive],
        outputs=[search_input, stats_table_html, user_selector, user_info_display, qr_code_display]
    )

    def search_table(query):
        table = update_table(True)
        if query:
            filtered_table = table.loc[
                table.apply(lambda row: query.lower() in " ".join(map(str, row)).lower(), axis=1)
            ]
            print(f"[DEBUG] Filtered table:\n{filtered_table}")
            return df_to_html(filtered_table)
        return df_to_html(table)

    search_input.change(
        fn=search_table,
        inputs=[search_input],
        outputs=[stats_table_html]
    )

    def find_qr_code(username):
        qr_code_file = QR_CODE_DIR / f"{username}.png"
        if qr_code_file.exists():
            return str(qr_code_file)
        return None

    def display_user_info(selected_user):
        if isinstance(selected_user, list):
            if len(selected_user) > 0:
                selected_user = selected_user[0]
            else:
                selected_user = "Select a user"

        if not selected_user or selected_user == "Select a user":
            return "", None

        user_info = show_user_info(selected_user)
        qr_code_path = find_qr_code(selected_user)
        print(f"[DEBUG] User info:\n{user_info}")
        print(f"[DEBUG] QR Code path for {selected_user}: {qr_code_path}")
        return user_info, qr_code_path

    user_selector.change(
        fn=display_user_info,
        inputs=[user_selector],
        outputs=[user_info_display, qr_code_display]
    )
