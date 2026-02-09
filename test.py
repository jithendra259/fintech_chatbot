from agents.data_agent import DataFetchAgent
from config.config import config

prices = DataFetchAgent.run(
    assets=config.assets,
    start_date=config.start_date,
    end_date=config.end_date,
    frequency=config.data_frequency
)

print(prices.head())
print(prices.tail())
