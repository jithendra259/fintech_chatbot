class AIReasoningAgent:
    @staticmethod
    def run(portfolio_result: dict) -> str:
        """
        Generate post-hoc explanation for the optimized portfolio.
        This agent does NOT influence optimization decisions.
        """

        weights = portfolio_result["weights"]
        expected_return = portfolio_result["expected_return"]
        risk = portfolio_result["risk"]

        # Identify dominant assets
        significant_assets = {
            asset: weight
            for asset, weight in weights.items()
            if weight > 0.01
        }

        explanation = []
        explanation.append(
            f"The optimized portfolio achieves an expected daily return of "
            f"{expected_return:.4f} with a corresponding risk of {risk:.4f}."
        )

        if len(significant_assets) == 1:
            asset, weight = next(iter(significant_assets.items()))
            explanation.append(
                f"The portfolio is highly concentrated in {asset}, which accounts "
                f"for approximately {weight:.1%} of the total allocation. "
                f"This concentration arises because {asset} exhibits a superior "
                f"risk-adjusted return relative to other assets in the universe."
            )
        else:
            explanation.append(
                "The portfolio allocation is distributed across multiple assets "
                "to balance expected returns and portfolio risk."
            )

        explanation.append(
            "This outcome reflects the inherent behavior of classical mean–variance "
            "optimization, which prioritizes assets with the highest contribution "
            "to expected return per unit of risk."
        )

        explanation.append(
            "No learning, forecasting, or adaptive decision-making mechanisms "
            "were employed in generating this explanation."
        )

        return " ".join(explanation)
