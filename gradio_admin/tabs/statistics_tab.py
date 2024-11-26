# gradio_admin/tabs/statistics_tab.py

import gradio as gr
from gradio_admin.functions.statistics import get_user_statistics  # Предполагаем, что эта функция уже реализована

def statistics_tab():
    with gr.Row():
        gr.Markdown("## Статистика пользователей")
    with gr.Column(scale=1, min_width=300):
        stats_output = gr.Textbox(label="Статистика", interactive=False)

        def fetch_statistics():
            return get_user_statistics()

        gr.Button("Обновить статистику").click(
            fetch_statistics,
            outputs=stats_output
        )
