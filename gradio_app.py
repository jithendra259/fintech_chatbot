import gradio as gr

from orchestrator.orchestrator import Orchestrator
from config.config import config


orchestrator = Orchestrator(config)


def start_session(selected_stocks):
    result = orchestrator.start_session(selected_stocks)
    if result["success"] is True:
        return (
            [],
            result["message"],
            gr.update(interactive=True),
            gr.update(interactive=True),
        )
    return (
        [],
        result["message"],
        gr.update(interactive=False),
        gr.update(interactive=False),
    )


def chat(user_message, history):
    history = history or []

    if user_message == "":
        return history, user_message

    result = orchestrator.chat(user_message)
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": result["response"]})
    return history, ""


def reset_session():
    orchestrator.reset_session()
    return (
        [],
        "Session reset. Select stocks and click Start Session.",
        gr.update(interactive=False),
        gr.update(interactive=False),
    )


with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# Supervisory Portfolio Assistant")
        gr.Markdown("Select stocks, start session, then ask questions.")

    with gr.Row():
        stock_selector = gr.CheckboxGroup(
            choices=config.assets,
            label="Select Stocks (choose 2 or more)",
            value=["AAPL", "MSFT", "GOOGL"],
        )

    with gr.Row():
        start_btn = gr.Button("Start Session", variant="primary")
        reset_btn = gr.Button("Reset Session", variant="secondary")

    with gr.Row():
        status_box = gr.Textbox(
            label="Status",
            value="Select stocks and click Start Session to begin.",
            interactive=False,
        )

    with gr.Row():
        chatbot = gr.Chatbot(
            label="Portfolio Assistant",
            height=400,
        )

    with gr.Row():
        msg_input = gr.Textbox(
            label="Your Question",
            placeholder="Ask about selected stocks...",
            interactive=False,
        )
        send_btn = gr.Button(
            "Send",
            variant="primary",
            interactive=False,
        )

    start_btn.click(
        fn=start_session,
        inputs=[stock_selector],
        outputs=[chatbot, status_box, msg_input, send_btn],
    )

    send_btn.click(
        fn=chat,
        inputs=[msg_input, chatbot],
        outputs=[chatbot, msg_input],
    )

    msg_input.submit(
        fn=chat,
        inputs=[msg_input, chatbot],
        outputs=[chatbot, msg_input],
    )

    reset_btn.click(
        fn=reset_session,
        inputs=[],
        outputs=[chatbot, status_box, msg_input, send_btn],
    )


if __name__ == "__main__":
    try:
        demo.launch(
            server_port=7860,
            share=False,
            show_error=True,
        )
    except OSError as error:
        if "Cannot find empty port in range: 7860-7860" in str(error):
            demo.launch(
                server_port=7861,
                share=False,
                show_error=True,
            )
        else:
            raise
