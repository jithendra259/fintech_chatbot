import gradio as gr

from config.config import config
from orchestrator.orchestrator import Orchestrator


orchestrator = Orchestrator(config)


CUSTOM_CSS = """
body, .gradio-container {
    background: #343541 !important;
    color: #ececf1 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", sans-serif !important;
}
#page-wrap {
    min-height: 90vh;
    width: 100%;
    max-width: 1200px;
    margin: 0 auto !important;
    padding: 20px !important;
    background: #343541 !important;
}
#chat-shell {
    width: 100%;
    margin: 0 auto;
    background: #343541 !important;
    border: none !important;
    border-radius: 12px !important;
    overflow: hidden;
}
#shell-head {
    padding: 16px 20px 8px 20px;
    background: #343541 !important;
    border-bottom: none !important;
}
.chat-tag {
    display: inline-block;
    font-size: 13px;
    font-weight: 600;
    color: #d1d5db;
    background: #443451;
    border: 1px solid #565869;
    border-radius: 6px;
    padding: 4px 10px;
}
#setup-acc {
    margin: 0 !important;
    background: transparent !important;
}
#chat-window {
    background: #343541 !important;
    border: none !important;
    padding: 16px !important;
    height: 520px !important;
}
#chat-window .message.user {
    background: #444654 !important;
    border: none !important;
    border-radius: 8px !important;
    color: #ececf1 !important;
    box-shadow: none !important;
    padding: 12px 16px !important;
}
#chat-window .message.bot {
    background: #343541 !important;
    border: none !important;
    border-radius: 8px !important;
    color: #ececf1 !important;
    box-shadow: none !important;
    padding: 12px 16px !important;
}
#toolbar-row {
    padding: 12px 16px 8px 16px !important;
    gap: 10px !important;
    margin-top: 8px !important;
    background: #343541 !important;
}
.tool-btn {
    background: #565869 !important;
    color: #ececf1 !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
.tool-btn:hover {
    background: #6d6e81 !important;
}
.top-primary {
    background: #1f1f1f !important;
    color: #ececf1 !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.top-primary:hover {
    background: #2d2d2d !important;
}
.top-secondary {
    background: #565869 !important;
    color: #ececf1 !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.top-secondary:hover {
    background: #6d6e81 !important;
}
#composer-row {
    padding: 12px 16px 16px 16px !important;
    gap: 10px !important;
    background: #343541 !important;
    border-top: none !important;
}
#message-box textarea {
    background: #40414f !important;
    color: #ececf1 !important;
    border: none !important;
    border-radius: 6px !important;
    min-height: 46px !important;
    padding: 10px 12px !important;
    transition: all 0.2s ease !important;
}
#message-box textarea:focus {
    background: #40414f !important;
    border: none !important;
    outline: 2px solid #565869 !important;
    outline-offset: 0 !important;
}
.submit-button {
    background: #1f1f1f !important;
    color: #ececf1 !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.submit-button:hover {
    background: #2d2d2d !important;
}
#status-box textarea {
    background: #40414f !important;
    color: #ececf1 !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 10px 12px !important;
}
"""


def _append_chat(history, user_message, result):
    response = result["response"]
    intent = result.get("intent", "")
    sections = result.get("sections_used", [])
    footer = f"\n\n---\n*Intent: {intent} | Sections: {', '.join(sections)}*"
    full_response = response + footer
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": full_response})
    return history


def _pop_last_turn(history):
    history = history or []
    if not history:
        return history

    if history and history[-1].get("role") == "assistant":
        history.pop()
    if history and history[-1].get("role") == "user":
        history.pop()

    if len(orchestrator.messages) > 1 and orchestrator.messages[-1].get("role") == "assistant":
        orchestrator.messages.pop()
    if len(orchestrator.messages) > 1 and orchestrator.messages[-1].get("role") == "user":
        orchestrator.messages.pop()

    return history


def start_session(selected_stocks):
    result = orchestrator.start_session(selected_stocks)
    if result["success"]:
        return (
            [],
            result["message"],
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(interactive=True),
            gr.update(visible=False),
        )
    return (
        [],
        result["message"],
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=True),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(visible=True),
    )


def chat(user_message, history):
    history = history or []
    if user_message == "":
        return history, user_message

    result = orchestrator.chat(user_message)
    history = _append_chat(history, user_message, result)
    return history, ""


def retry_last(history):
    history = history or []
    last_user = None
    for msg in reversed(history):
        if msg.get("role") == "user":
            last_user = msg.get("content")
            break

    if not last_user:
        return history, "No previous user message to retry."

    history = _pop_last_turn(history)
    result = orchestrator.chat(last_user)
    history = _append_chat(history, last_user, result)
    return history, "Retried last message."


def undo_last(history):
    history = _pop_last_turn(history or [])
    return history, "Last turn removed."


def clear_chat():
    if orchestrator.messages:
        orchestrator.messages = [orchestrator.messages[0]]
    return [], "Conversation cleared."


def reset_session():
    orchestrator.reset_session()
    return (
        [],
        "Session reset. Select stocks and click Start Analysis.",
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=True),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(visible=True),
    )


with gr.Blocks() as demo:
    with gr.Column(elem_id="page-wrap"):
        with gr.Column(elem_id="chat-shell"):
            with gr.Row(elem_id="shell-head"):
                gr.Markdown("<span class='chat-tag'>Chatbot</span>")

            with gr.Accordion("Session Setup", open=False, elem_id="setup-acc") as setup_acc:
                stock_selector = gr.CheckboxGroup(
                    choices=config.assets,
                    label="Select Stocks (choose 2 or more)",
                    value=["AAPL", "MSFT", "GOOGL"],
                )
                with gr.Row():
                    start_btn = gr.Button("Start Analysis", elem_classes=["top-primary"])
                    reset_btn = gr.Button("Reset", elem_classes=["top-secondary"])
                status_box = gr.Textbox(
                    label="System Status",
                    value="Select stocks and click Start Analysis to begin.",
                    interactive=False,
                    lines=2,
                    elem_id="status-box",
                )

            chatbot = gr.Chatbot(
                label=None,
                height=620,
                buttons=["copy"],
                elem_id="chat-window",
            )

            with gr.Row(elem_id="toolbar-row"):
                retry_btn = gr.Button("Retry", elem_classes=["tool-btn"], interactive=False)
                undo_btn = gr.Button("Undo", elem_classes=["tool-btn"], interactive=False)
                clear_btn = gr.Button("Clear", elem_classes=["tool-btn"], interactive=False)

            with gr.Row(elem_id="composer-row"):
                msg_input = gr.Textbox(
                    show_label=False,
                    placeholder="Type a message...",
                    interactive=False,
                    lines=1,
                    elem_id="message-box",
                    container=False,
                    scale=8,
                )
                send_btn = gr.Button(
                    "Submit",
                    elem_classes=["submit-button"],
                    interactive=False,
                    scale=1,
                )

    start_btn.click(
        fn=start_session,
        inputs=[stock_selector],
        outputs=[chatbot, status_box, msg_input, send_btn, reset_btn, retry_btn, undo_btn, clear_btn, setup_acc],
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

    retry_btn.click(
        fn=retry_last,
        inputs=[chatbot],
        outputs=[chatbot, status_box],
    )

    undo_btn.click(
        fn=undo_last,
        inputs=[chatbot],
        outputs=[chatbot, status_box],
    )

    clear_btn.click(
        fn=clear_chat,
        inputs=[],
        outputs=[chatbot, status_box],
    )

    reset_btn.click(
        fn=reset_session,
        inputs=[],
        outputs=[chatbot, status_box, msg_input, send_btn, reset_btn, retry_btn, undo_btn, clear_btn, setup_acc],
    )


if __name__ == "__main__":
    try:
        demo.launch(
            server_port=7860,
            share=False,
            show_error=True,
            theme=gr.themes.Soft(),
            css=CUSTOM_CSS,
        )
    except OSError as error:
        if "Cannot find empty port in range: 7860-7860" in str(error):
            demo.launch(
                server_port=7861,
                share=False,
                show_error=True,
                theme=gr.themes.Soft(),
                css=CUSTOM_CSS,
            )
        else:
            raise
