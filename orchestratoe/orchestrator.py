from agents.data_agent import DataFetchAgent
from agents.data_alignment_agent import DataAlignmentAgent
from agents.optimization_agent import optimisationagent as OptimizationAgent
from agents.ai_reasoning_agent import AIReasoningAgent
from agents.performance_evaluator import PerformanceEvaluator


class Orchestrator:
    def __init__(self, config):
        self.config = config

    def run_pipeline(self):

        # -----------------------------------
        # Step 1: Fetch full dataset
        # -----------------------------------
        raw_data = DataFetchAgent.run(
            assets=self.config.assets,
            start_date=self.config.start_date,
            end_date=self.config.end_date,
            frequency=self.config.data_frequency
        )

        aligned_data = DataAlignmentAgent.run(raw_data)
        returns = aligned_data["returns"]

        # -----------------------------------
        # Step 2: Train-Test Split
        # -----------------------------------
        train_returns = returns.loc[:self.config.train_end]
        test_returns = returns.loc[self.config.test_start:]

        # Recompute statistics ONLY on training data
        train_mean = train_returns.mean()
        train_cov = train_returns.cov()

        train_aligned = {
            "returns": train_returns,
            "mean_returns": train_mean,
            "covariance": train_cov
        }

        # -----------------------------------
        # Step 3: Optimize on TRAIN
        # -----------------------------------
        portfolio_result = OptimizationAgent.run(
            aligned_data=train_aligned,
            risk_aversion=self.config.risk_aversion
        )

        # -----------------------------------
        # Step 4: Evaluate
        # -----------------------------------
        in_sample_eval = PerformanceEvaluator.evaluate_with_benchmark(
            train_returns,
            portfolio_result["weights"]
        )

        out_sample_eval = PerformanceEvaluator.evaluate_with_benchmark(
            test_returns,
            portfolio_result["weights"]
        )

        explanation = AIReasoningAgent.run(portfolio_result)

        return {
            "portfolio_result": portfolio_result,
            "in_sample_evaluation": in_sample_eval,
            "out_sample_evaluation": out_sample_eval,
            "explanation": explanation
        }
