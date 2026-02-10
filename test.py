from agents.data_agent import DataFetchAgent
from config.config import config
from agents.data_alignment_agent import DataAlignmentAgent

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
