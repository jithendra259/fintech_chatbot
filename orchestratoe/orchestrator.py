from agents.data_agent import DataFetchAgent
from agents.data_alignment_agent import DataAlignmentAgent
from agents.optimization_agent import optimisationagent as OptimizationAgent
from agents.ai_reasoning_agent import AIReasoningAgent
from agents.performance_evaluator import PerformanceEvaluator


class Orchestrator:
    def __init__(self, config):
        self.config = config

    def run_pipeline(self):

        # ---------------------------
        # Step 1: Fetch raw price data
        # ---------------------------
        raw_data = DataFetchAgent.run(
            assets=self.config.assets,
            start_date=self.config.start_date,
            end_date=self.config.end_date,
            frequency=self.config.data_frequency
        )

        # ---------------------------
        # Step 2: Align data and compute statistics
        # ---------------------------
        aligned_data = DataAlignmentAgent.run(raw_data)

        # ---------------------------
        # Step 3: Portfolio optimization
        # ---------------------------
        portfolio_result = OptimizationAgent.run(
            aligned_data=aligned_data,
            risk_aversion=self.config.risk_aversion
        )

        # ---------------------------
        # Step 4: Evaluate performance
        # (Optimized vs Equal Weight)
        # ---------------------------
        evaluation = PerformanceEvaluator.evaluate_with_benchmark(
            aligned_data["returns"],
            portfolio_result["weights"]
        )

        # ---------------------------
        # Step 5: AI Explanation
        # ---------------------------
        explanation = AIReasoningAgent.run(portfolio_result)

        return {
            "raw_data": raw_data,
            "aligned_data": aligned_data,
            "portfolio_result": portfolio_result,
            "evaluation": evaluation,
            "explanation": explanation
        }
