from config.config import config
from orchestratoe.orchestrator import Orchestrator
if __name__ == "__main__":
    orchestrator = Orchestrator(config)
    result = orchestrator.run_pipeline()

    print(result["portfolio_result"])
    print(result["explanation"])
    print("\nPerformance Comparison:")

    for portfolio_type, metrics in result["evaluation"].items():
        print(f"\n{portfolio_type.upper()} PORTFOLIO:")
        
        for metric_name, value in metrics.items():
            if metric_name != "cumulative_returns":
                print(f"{metric_name}: {value:.4f}")

