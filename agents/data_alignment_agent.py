import numpy as np
import pandas as pd


class DataAlignmentAgent:
    @staticmethod
    def run(price_data: pd.DataFrame):
        # 1. Ensure datetime index
        price_data = price_data.copy()
        price_data.index = pd.to_datetime(price_data.index)

        # 2. Drop dates where all assets are missing
        price_data = price_data.dropna(how="all")

        # 3. Forward-fill then backward-fill small gaps
        price_data = price_data.ffill().bfill()

        # 4. Drop any remaining NaNs (safety)
        price_data = price_data.dropna()

        # 5. Compute log returns
        log_returns = np.log(price_data / price_data.shift(1)).dropna()

        # 6. Estimate expected returns and covariance
        mean_returns = log_returns.mean()
        covariance = log_returns.cov()

        return {
            "prices": price_data,
            "returns": log_returns,
            "mean_returns": mean_returns,
            "covariance": covariance
        }
