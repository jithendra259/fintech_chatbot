class config:
    assets = [
    "AAPL", "MSFT", "GOOGL", "AMZN",  # Technology
    "TSLA", "META",                           # Consumer Discretionary / Comm
    "JPM", "V", "MA", "BAC",                  # Financial
    "WMT", "KO", "PG",                        # Consumer Staples
    "JNJ", "PFE", "UNH",                      # Healthcare
    "XOM", "CVX",                             # Energy
    "DIS"                                     # Entertainment
]
    start_date="2015-01-01"
    end_date="2025-12-30"

    train_end = "2021-12-31"
    test_start = "2022-01-01"


    data_frequency="daily"

    risk_aversion=1
