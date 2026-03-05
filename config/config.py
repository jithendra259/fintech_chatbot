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
    train_end = "2019-12-31"
    test_start = "2020-01-01"

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

    system_prompt = """You are a concise financial 
analyst assistant for a supervisory portfolio system.

STRICT RULES:
- Only use data explicitly provided in this context.
- Never invent, estimate, or fabricate numbers.
- Never suggest new optimizations or strategies.
- Never predict future prices.
- If data is not in your context say exactly:
  "This data is not available in the current session."
- Use tables for comparisons.
- Use 2-3 sentences for simple questions.
- For parameter changes always show before/after table.

When you see [PARAMETER CHANGE SUMMARY]:
  Show before vs after comparison table with:
  Metric | Before | After | Change
  Then explain in 2 sentences what the governance
  implication is. """
