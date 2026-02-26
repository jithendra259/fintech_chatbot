class config:
    assets = [
        "AAPL", "MSFT", "GOOGL", "AMZN",
        "JPM", "BAC", "GS", "MS",
        "XOM", "CVX", "COP",
        "JNJ", "PFE", "UNH",
        "PG", "KO", "PEP",
        "CAT", "BA"
    ]

    start_date = "2010-01-01"
    end_date = "2024-12-31"
    train_end = "2022-12-31"
    test_start = "2023-01-01"

    data_frequency = "daily"
    risk_aversion = 3.0
    theta_H = 1.0
    inst_window = 60
    train_window = 504
    test_window = 63

    ollama_model = "phi3.5"
    ollama_url = "http://localhost:11434"
    ollama_keep_alive = "10m"
    conversation_window = 6

    data_dir = "data"
    baseline_stats_path = "data/baseline_stats.json"
    research_cache_path = "data/research_cache.json"
    weights_history_path = "data/weights_history.json"

    system_prompt = """You are a financial analyst assistant.
   You have access to stock price data for the selected assets.
   Answer questions about the stocks clearly and analytically.
   Do not give investment advice.
   Do not recommend buying or selling.
   Only explain and analyse what you are given."""
