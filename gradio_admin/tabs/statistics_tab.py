#!/usr/bin/env python3
# gradio_admin/tabs/statistics_tab.py
# Вкладка для просмотра статистики пользователей WireGuard

import gradio as gr
from gradio_admin.functions.statistics import get_user_statistics

def statistics_tab():
    """
    Вкладка для отображения статистики пользователей WireGuard.
    """
    refresh_button = gr.Button("Обновить статистику")
    statistics_output = gr.Textbox(label="Статистика пользователей", interactive=False)

    def handle_refresh_statistics():
        return get_user_statistics()

    refresh_button.click(
        handle_refresh_statistics,
        inputs=[],
        outputs=statistics_output
    )
    
    return [refresh_button, statistics_output]
