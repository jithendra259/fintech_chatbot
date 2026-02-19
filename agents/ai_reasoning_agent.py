import requests
import json


class AIReasoningAgent:
    """
    Post-hoc portfolio explanation using Ollama Gemini Flash.
    This agent does NOT influence optimization decisions.
    """

    @staticmethod
    def run(portfolio_result: dict) -> str:

        # Clean weights (convert to % and remove near-zero noise)
        cleaned_weights = {
            asset: round(weight * 100, 2)
            for asset, weight in portfolio_result["weights"].items()
            if weight > 1e-6
        }

        expected_return = portfolio_result["expected_return"]
        risk = portfolio_result["risk"]

        prompt = f"""
You are a professional financial analyst.

Explain the following optimized stock portfolio clearly and analytically.

Portfolio Weights (in %):
{json.dumps(cleaned_weights, indent=2)}

Expected daily return: {expected_return:.6f}
Portfolio variance: {risk:.6f}

Constraints:
- Do NOT suggest changes
- Do NOT propose strategies
- Do NOT recommend rebalancing
- Do NOT provide investment advice
- Only explain why this allocation occurred
- Keep explanation concise
"""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemini-3-flash-preview",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        return response.json()["response"].strip()
