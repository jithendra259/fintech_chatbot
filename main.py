from config.config import config
from orchestratoe.orchestrator import Orchestrator
if __name__ == "__main__":
    orchestrator = Orchestrator(config)
    result = orchestrator.run_pipeline()

    print(result["portfolio_result"])
    print(result["explanation"])
    print("\nPerformance Comparison:")

    print("\nIN-SAMPLE PERFORMANCE:")
    for portfolio_type, metrics in result["in_sample_evaluation"].items():
        print(f"\n{portfolio_type.upper()} PORTFOLIO:")
        for k, v in metrics.items():
            if k != "cumulative_returns":
                print(f"{k}: {v:.4f}")

    print("\nOUT-OF-SAMPLE PERFORMANCE:")
    for portfolio_type, metrics in result["out_sample_evaluation"].items():
        print(f"\n{portfolio_type.upper()} PORTFOLIO:")
        for k, v in metrics.items():
            if k != "cumulative_returns":
                print(f"{k}: {v:.4f}")


