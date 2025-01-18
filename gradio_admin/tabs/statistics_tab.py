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
    # Fetch initial data
    def get_initial_data():
        update_traffic_data(USER_DB_PATH)
        table = update_table(True)
        user_list = ["Select a user"] + table["👤 User"].tolist() if not table.empty else ["Select a user"]
        return table, user_list

    initial_table, initial_user_list = get_initial_data()

    with gr.Row():
        gr.Markdown("## Statistics")

    # Show inactive checkbox and Refresh button
    with gr.Row():
        show_inactive = gr.Checkbox(label="Show blocked", value=True)
        refresh_button = gr.Button("Refresh")

    # Search field
    with gr.Row():
        search_input = gr.Textbox(label="Search", placeholder="Enter text to filter table...", interactive=True)

    # User selection and display of information and QR code
    with gr.Row(equal_height=True):
        with gr.Column(scale=3):  # Left column for User Details
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
        with gr.Column(scale=1, min_width=200):  # Right column for QR code
            qr_code_display = gr.Image(
                label="User QR Code",
                type="filepath",
                interactive=False,
                height=200  # Fixed height for proportional view
            )

    # Data table
    with gr.Row():
        stats_table = gr.Dataframe(
            headers=["👤 User", "📊 Used", "📦 Limit", "🌐 IP Address", "⚡ St.", "💳 $", "UID"],
            value=initial_table,
            interactive=False,
            wrap=True
        )

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
        # Reset user_info_display, user_selector, and qr_code_display
        return "", table, gr.update(choices=user_list, value="Select a user"), "", None

    # Refresh table on button click
    refresh_button.click(
        fn=refresh_table,
        inputs=[show_inactive],
        outputs=[search_input, stats_table, user_selector, user_info_display, qr_code_display]
    )

    # Function to search within the table
    def search_table(query):
        table = update_table(True)  # Load the original table
        if query:
            # Filter the table across all columns
            filtered_table = table.loc[
                table.apply(lambda row: query.lower() in " ".join(map(str, row)).lower(), axis=1)
            ]
            print(f"[DEBUG] Filtered table:\n{filtered_table}")
            return filtered_table
        return table  # Return the original table if query is empty

    # Search in the table
    search_input.change(
        fn=search_table,
        inputs=[search_input],
        outputs=[stats_table]
    )

    # Function to find a user's QR code
    def find_qr_code(username):
        """
        Finds the path to a user's QR code.
        :param username: User's name
        :return: Path to the QR code file or None if the file is not found.
        """
        qr_code_file = QR_CODE_DIR / f"{username}.png"
        if qr_code_file.exists():
            return str(qr_code_file)
        return None

    # Display user information and their QR code
    def display_user_info(selected_user):
        # Ensure selected_user is a string, not a list
        if isinstance(selected_user, list):
            if len(selected_user) > 0:
                selected_user = selected_user[0]
            else:
                selected_user = "Select a user"

        # If "Select a user" is chosen, return empty strings
        if not selected_user or selected_user == "Select a user":
            return "", None

        # Retrieve user information
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
