import ollama
import pandas as pd

from config.config import config


class AIReasoningAgent:
    @staticmethod
    def build_system_message(selected_stocks: list, price_data: pd.DataFrame) -> dict:
        first_date = price_data.index[0]
        last_date = price_data.index[-1]
        first_row = price_data.iloc[0]
        last_row = price_data.iloc[-1]

        latest_price_lines = []
        price_change_lines = []
        for stock in selected_stocks:
            first_price = float(first_row[stock])
            last_price = float(last_row[stock])
            change_pct = ((last_price - first_price) / first_price) * 100

            latest_price_lines.append(f"- {stock}: {last_price:.2f}")
            price_change_lines.append(f"- {stock}: {change_pct:.2f}%")

        stock_summary = (
            "\n\nStock Data Summary:\n"
            f"Selected stocks: {selected_stocks}\n"
            f"Date range: {first_date} to {last_date}\n"
            "Latest closing prices:\n"
            + "\n".join(latest_price_lines)
            + "\nPrice change over period:\n"
            + "\n".join(price_change_lines)
        )

        system_prompt_string = f"{config.system_prompt}{stock_summary}"
        return {"role": "system", "content": system_prompt_string}

    @staticmethod
    def chat(messages: list, user_message: str) -> dict:
        user_entry = {"role": "user", "content": user_message}

        if messages:
            system_message = messages[0]
            history_tail = messages[1:][-config.conversation_window:]
            windowed_messages = [system_message] + history_tail
        else:
            windowed_messages = []

        windowed_messages.append(user_entry)

        try:
            response = ollama.chat(
                model=config.ollama_model,
                messages=windowed_messages,
                keep_alive=config.ollama_keep_alive,
                stream=False,
            )
        except Exception:
            return {
                "response": "LLM unavailable. Ollama is not running. Start Ollama with: ollama serve",
                "updated_messages": messages,
            }

        if isinstance(response, dict):
            response_text = response.get("message", {}).get("content", "")
        else:
            response_text = getattr(getattr(response, "message", None), "content", "")

        assistant_entry = {"role": "assistant", "content": response_text}
        updated_messages = list(messages) + [user_entry, assistant_entry]

        return {"response": response_text, "updated_messages": updated_messages}
