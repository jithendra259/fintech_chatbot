import requests
import json


class AIReasoningAgent:
    @staticmethod
    def run(portfolio_result: dict) -> str:
        """
        Post-hoc portfolio explanation using a local Ollama model (Mistral).
        This agent does NOT influence optimization decisions.
        """

        weights = portfolio_result["weights"]
        expected_return = portfolio_result["expected_return"]
        risk = portfolio_result["risk"]

        prompt = f"""
You are a financial analyst.

Explain the following optimized stock portfolio in clear, professional English.

Portfolio weights:
{json.dumps(weights, indent=2)}

Expected daily return: {expected_return:.4f}
Portfolio risk (variance): {risk:.4f}

Constraints:
- Do NOT suggest changes
- Do NOT propose strategies
- Do NOT recommend rebalancing
- Only explain why this allocation occurred
- Keep the explanation concise
"""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            },
            timeout=300
        )

        response.raise_for_status()

        return response.json()["response"]
