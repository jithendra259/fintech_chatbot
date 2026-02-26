import numpy as np
import pandas as pd
from config.config import config


class DataAlignmentAgent:
    @staticmethod
    def run(price_data: pd.DataFrame):
        try:
            prices = price_data.copy()
            prices.index = pd.to_datetime(prices.index)
            prices = prices.dropna(how="all")
            prices = prices.ffill()
            prices = prices.bfill()
            prices = prices.dropna()

            full_returns = np.log(prices / prices.shift(1)).dropna()

            train_returns = full_returns.loc[:config.train_end]
            test_returns = full_returns.loc[config.test_start:]

            if train_returns.empty:
                raise ValueError(f"No training data found before {config.train_end}")

            if test_returns.empty:
                raise ValueError(f"No test data found after {config.test_start}")

            mean_returns = train_returns.mean()
            covariance = train_returns.cov()

            return {
                "prices": prices,
                "full_returns": full_returns,
                "train_returns": train_returns,
                "test_returns": test_returns,
                "mean_returns": mean_returns,
                "covariance": covariance,
                "assets": list(full_returns.columns),
                "train_start": str(train_returns.index[0].date()),
                "train_end": str(train_returns.index[-1].date()),
                "test_start": str(test_returns.index[0].date()),
                "test_end": str(test_returns.index[-1].date()),
                "n_train_days": len(train_returns),
                "n_test_days": len(test_returns),
                "n_assets": len(full_returns.columns),
            }
        except Exception as error:
            raise ValueError(f"DataAlignmentAgent failed: {str(error)}") from error
