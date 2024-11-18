import gradio as gr
from gradio_admin.create_user import create_user
from gradio_admin.list_users import list_users
from gradio_admin.delete_user import delete_user
from gradio_admin.search_user import search_user

with gr.Blocks() as admin_interface:
    with gr.Tab("Создание и список"):
        with gr.Row():
            username_input = gr.Textbox(label="Имя пользователя")
            create_button = gr.Button("Создать")
            create_output = gr.Textbox(label="Результат создания")
            create_button.click(create_user, inputs=username_input, outputs=create_output)
        
        with gr.Row():
            list_button = gr.Button("Показать пользователей")
            list_output = gr.Textbox(label="Список пользователей", interactive=False)
            list_button.click(list_users, outputs=list_output)

    with gr.Tab("Удаление пользователей"):
        delete_input = gr.Textbox(label="Имя пользователя для удаления")
        delete_button = gr.Button("Удалить")
        delete_output = gr.Textbox(label="Результат удаления")
        delete_button.click(delete_user, inputs=delete_input, outputs=delete_output)
        
        with gr.Row():
            list_button = gr.Button("Показать пользователей")
            list_output = gr.Textbox(label="Список пользователей", interactive=False)
            list_button.click(list_users, outputs=list_output)

    with gr.Tab("Поиск пользователей"):
        search_input = gr.Textbox(label="Введите имя или IP")
        search_button = gr.Button("Поиск")
        search_output = gr.Textbox(label="Результат поиска")
        search_button.click(search_user, inputs=search_input, outputs=search_output)

if __name__ == "__main__":
    admin_interface.launch(server_name="0.0.0.0", server_port=7860, share=True)
