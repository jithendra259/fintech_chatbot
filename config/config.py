class Config:
    assets = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",  # Technology
    "TSLA", "META",                           # Consumer Discretionary / Comm
    "JPM", "V", "MA", "BAC",                  # Financial
    "WMT", "KO", "PG",                        # Consumer Staples
    "JNJ", "PFE", "UNH",                      # Healthcare
    "XOM", "CVX",                             # Energy
    "DIS"                                     # Entertainment
]
    start_date="2015-01-01"
    end_date="2025-12-30"

    data_frequency="daily"

    risk_aversion=1
