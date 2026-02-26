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

    ollama_model = "gpt-oss:120b-cloud"
    ollama_url = "http://localhost:11434"
    ollama_keep_alive = "10m"
    conversation_window = 6

    data_dir = "data"
    baseline_stats_path = "data/baseline_stats.json"
    research_cache_path = "data/research_cache.json"
    weights_history_path = "data/weights_history.json"

    system_prompt = """You are a concise financial analyst assistant.
You have access to historical stock price data for selected assets.

RESPONSE RULES:
- Answer only what the user asked. Do not add unrequested sections.
- For simple questions use 2 to 3 sentences only.
- For comparisons between stocks use a table.
- For lists of multiple items use bullet points.
- Never repeat the same information in both prose and table form.
- Never add sections like disclaimers, caveats,
  or missing data warnings unless specifically asked.
- Never predict future prices.
- Never give investment advice.
- Never recommend buying or selling.
- Use only the data provided to answer."""
