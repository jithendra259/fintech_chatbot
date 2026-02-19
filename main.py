from config.config import config
from orchestratoe.orchestrator import Orchestrator
if __name__ == "__main__":
    orchestrator = Orchestrator(config)
    result = orchestrator.run_pipeline()

    print(result["portfolio_result"])
    print(result["explanation"])
    print("\nPerformance Metrics:")
    for k, v in result["evaluation"].items():
        if k != "cumulative_returns":
            print(f"{k}: {v:.4f}")

