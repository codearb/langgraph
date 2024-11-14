import gradio as gr
from workflow_graph import chat_bot

def main():
    with gr.Blocks() as demo:
        with gr.Column():
            gr.Markdown("# Restaurants ChatBot")
            user_id = gr.Textbox(label="User ID", value="3")
            question = gr.Textbox(label="Enter your question")
            submit = gr.Button("Submit")

        with gr.Column():
            output = gr.Textbox(label="Response", max_lines=10)

        submit.click(
            fn=lambda user_id, question: chat_bot(user_id, question),
            inputs=[user_id, question],
            outputs=[output]
        )

    demo.launch()

if __name__ == "__main__":
    main()