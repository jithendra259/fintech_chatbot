from config.config import config
from agents.data_agent import DataFetchAgent
from agents.ai_reasoning_agent import AIReasoningAgent


class Orchestrator:
    def __init__(self, config):
        self.config = config
        self.price_data = None
        self.selected_stocks = []
        self.messages = []
        self.session_active = False

    def start_session(self, selected_stocks: list) -> dict:
        try:
            if not selected_stocks:
                return {
                    "success": False,
                    "message": "No stocks selected. Please select at least one stock.",
                }

            for stock in selected_stocks:
                if stock not in config.assets:
                    return {
                        "success": False,
                        "message": f"Invalid stock: {stock}. Choose from config assets.",
                    }

            self.price_data = DataFetchAgent.run(
                assets=selected_stocks,
                start_date=config.start_date,
                end_date=config.end_date,
                frequency=config.data_frequency,
            )

            self.selected_stocks = selected_stocks
            system_message = AIReasoningAgent.build_system_message(
                selected_stocks, self.price_data
            )
            self.messages = [system_message]
            self.session_active = True

            return {
                "success": True,
                "message": f"Session started for {selected_stocks}. You can now ask questions.",
            }
        except Exception as error:
            return {"success": False, "message": str(error)}

    def chat(self, user_message: str) -> dict:
        try:
            if not self.session_active:
                return {
                    "success": False,
                    "response": "No active session. Please select stocks first.",
                }

            if user_message == "":
                return {"success": False, "response": "Please type a message."}

            result = AIReasoningAgent.chat(
                messages=self.messages,
                user_message=user_message,
            )
            self.messages = result["updated_messages"]

            return {"success": True, "response": result["response"]}
        except Exception as error:
            return {"success": False, "response": f"Error: {str(error)}"}

    def reset_session(self) -> dict:
        self.price_data = None
        self.selected_stocks = []
        self.messages = []
        self.session_active = False
        return {"success": True, "message": "Session reset successfully."}
