import gradio as gr

from orchestrator.orchestrator import Orchestrator
from config.config import config


orchestrator = Orchestrator(config)


def start_session(selected_stocks):
    result = orchestrator.start_session(selected_stocks)
    if result["success"]:
        return (
            [],
            result["message"],
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True),
        )
    return (
        [],
        result["message"],
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
    )


def chat(user_message, history):
    history = history or []
    if user_message == "":
        return history, user_message

    result = orchestrator.chat(user_message)
    response = result["response"]
    intent = result.get("intent", "")
    sections = result.get("sections_used", [])
    footer = f"\n\n---\n*Intent: {intent} | Sections: {', '.join(sections)}*"
    full_response = response + footer

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": full_response})
    return history, ""


def reset_session():
    orchestrator.reset_session()
    return (
        [],
        "Session reset. Select stocks and click Start Session.",
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
    )


with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown("# Supervisory Portfolio Assistant")
        gr.Markdown("Regime-based governance with shrinkage estimation")

    with gr.Row():
        stock_selector = gr.CheckboxGroup(
            choices=config.assets,
            label="Select Stocks (choose 2 or more)",
            value=["AAPL", "MSFT", "GOOGL"],
        )

    with gr.Row():
        start_btn = gr.Button(
            "Start Analysis",
            variant="primary",
        )
        reset_btn = gr.Button(
            "Reset",
            variant="secondary",
        )

    with gr.Row():
        status_box = gr.Textbox(
            label="System Status",
            value="Select stocks and click Start Analysis to begin.",
            interactive=False,
            lines=2,
        )

    with gr.Row():
        chatbot = gr.Chatbot(
            label="Portfolio Assistant",
            height=450,
            buttons=["copy"],
        )

    with gr.Row():
        msg_input = gr.Textbox(
            label="Ask a question",
            placeholder="e.g. What is the current regime? Change lambda to 1.",
            interactive=False,
            lines=1,
        )
        send_btn = gr.Button(
            "Send",
            variant="primary",
            interactive=False,
        )

    with gr.Row():
        gr.Examples(
            examples=[
                "What is the current regime?",
                "Show me the portfolio weights",
                "What is the Sharpe ratio?",
                "Compare optimized vs equal weight",
                "Change lambda to 1",
                "Change theta to 0.5",
                "Change theta back to 1.0",
                "What is the instability index?",
                "What happened in the test period?",
            ],
            inputs=msg_input,
        )

    start_btn.click(
        fn=start_session,
        inputs=[stock_selector],
        outputs=[chatbot, status_box, msg_input, send_btn, reset_btn],
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
        outputs=[chatbot, status_box, msg_input, send_btn, reset_btn],
    )


if __name__ == "__main__":
    try:
        demo.launch(
            server_port=7860,
            share=False,
            show_error=True,
            theme=gr.themes.Soft(),
        )
    except OSError as error:
        if "Cannot find empty port in range: 7860-7860" in str(error):
            demo.launch(
                server_port=7861,
                share=False,
                show_error=True,
                theme=gr.themes.Soft(),
            )
        else:
            raise
