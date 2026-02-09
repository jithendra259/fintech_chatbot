import numpy as np 
import pandas as pd

class Dataalignmentagent:
    @staticmethod
    def run(price_data:pd.Dataframe):
        #1 datetime index
        price_data=price_data.copy()
        price_data.index=pd.to_datetime(price_data.index)

        #2 Drop dates where all assets are missing 
        price_data=price_data.dropna(how="all")

        #3 forward fill then backward-fill small gaps 
        price_data=price_data.ffill().bfill()

        #4 drop any remaining Nans(safety)
        price_data=price_data.dropna()

        #5 Compute log returns 
        log_returns=np.log(price_data/price_data.shift(1)).dropna()

        #6 estimateexpecrted returns and covariance
        mean_returns =log_returns.mean()
        covariance=log_returns.cov()

        return{
            "prices":price_data,
            "returns":log_returns,
            "mean_returns":mean_returns,
            "covariance":covariance
        }