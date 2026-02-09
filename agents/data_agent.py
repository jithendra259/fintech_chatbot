import yfinance as yf
import pandas as pd


class DataFetchAgent:
    @staticmethod
    def run(assets, start_date, end_date, frequency="daily"):
        if frequency != "daily":
            raise ValueError("Only daily frequency is supported")

        price_data = pd.DataFrame()

        for ticker in assets:
            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                auto_adjust=False,
                progress=False
            )

            if data.empty:
                raise ValueError(f"No data available for ticker {ticker}")

            #  Robust extraction of Adjusted Close
            if isinstance(data.columns, pd.MultiIndex):
                adj_close = data.xs("Adj Close", axis=1, level=0)
            else:
                adj_close = data["Adj Close"]

            # If xs returns a DataFrame, reduce to Series
            if isinstance(adj_close, pd.DataFrame):
                adj_close = adj_close.iloc[:, 0]

            price_data[ticker] = adj_close

        return price_data
