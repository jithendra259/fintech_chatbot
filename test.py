from agents.data_agent import DataFetchAgent
from config.config import config
from agents.data_alignment_agent import DataAlignmentAgent
from agents.optimization_agent import optimisationagent as OptimizationAgent

prices = DataFetchAgent.run(
    assets=config.assets,
    start_date=config.start_date,
    end_date=config.end_date,
    frequency=config.data_frequency
)

print(prices.head())
print(prices.tail())

aligned=DataAlignmentAgent.run(prices)
print("prices",aligned["prices"].head())
print(aligned["returns"].head())
print(aligned["mean_returns"])
print(aligned["covariance"].shape)

# Step 3: Optimize portfolio
result = OptimizationAgent.run(
    aligned_data=aligned,
    risk_aversion = config.risk_aversion

)

print("Optimal Weights:")
for k, v in result["weights"].items():
    print(f"{k}: {v:.4f}")

print("\nExpected Return:", result["expected_return"])
print("Portfolio Risk:", result["risk"])