from config.config import config
from orchestratoe.orchestrator import Orchestrator
if __name__ == "__main__":
    orchestrator = Orchestrator(config)
    result = orchestrator.run_pipeline()

    print(result["portfolio_result"])
    print(result["explanation"])
