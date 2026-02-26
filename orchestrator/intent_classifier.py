import re


INTENTS = [
    "regime_query",
    "metric_query",
    "allocation_query",
    "concept_query",
    "comparison_query",
    "parameter_change",
    "historical_query",
    "general_query",
]


INTENT_PATTERNS = {
    "regime_query": [
        "regime",
        "instability",
        "equal weight",
        "shrunk",
        "stress",
        "threshold",
        "signal",
        "switch",
        "above threshold",
        "below threshold",
        "governance",
        "theta",
    ],
    "metric_query": [
        "sharpe",
        "drawdown",
        "calmar",
        "volatility",
        "return",
        "performance",
        "risk",
        "metric",
        "ratio",
        "annualized",
        "how good",
        "how bad",
    ],
    "allocation_query": [
        "weight",
        "allocation",
        "invest",
        "holding",
        "position",
        "portfolio",
        "how much",
        "percentage",
        "percent",
        "hhi",
        "concentration",
        "effective n",
        "diversif",
    ],
    "concept_query": [
        "what is",
        "explain",
        "define",
        "meaning",
        "how does",
        "why is",
        "what does",
        "tell me about",
        "instability index",
        "shrinkage",
        "james stein",
        "ledoit wolf",
        "mean variance",
        "governance stability",
    ],
    "comparison_query": [
        "compare",
        "versus",
        "vs",
        "better",
        "worse",
        "difference",
        "benchmark",
        "equal weight vs",
        "optimized vs",
        "which is",
    ],
    "parameter_change": [
        "change",
        "set",
        "update",
        "modify",
        "adjust",
        "increase",
        "decrease",
        "lambda",
        "theta",
        "risk aversion",
        "threshold to",
        "make it",
        "use",
    ],
    "historical_query": [
        "history",
        "historical",
        "past",
        "previous",
        "before",
        "trend",
        "over time",
        "period",
        "training",
        "test period",
        "date",
        "when",
    ],
}


SECTION_MAP = {
    "regime_query": ["instability", "regime"],
    "metric_query": ["performance", "benchmark"],
    "allocation_query": ["weights", "optimization", "data_info"],
    "concept_query": ["instability", "regime", "shrinkage", "governance_note"],
    "comparison_query": ["performance", "benchmark", "weights"],
    "parameter_change": ["regime", "optimization", "performance", "params"],
    "historical_query": ["performance", "data_info", "instability"],
    "general_query": [
        "instability",
        "regime",
        "weights",
        "performance",
        "benchmark",
        "shrinkage",
        "data_info",
    ],
}


def classify_intent(query: str) -> dict:
    query_lower = query.lower()
    scores = {}

    for intent in INTENTS:
        keywords = INTENT_PATTERNS.get(intent, [])
        score = sum(1 for keyword in keywords if keyword in query_lower)
        scores[intent] = score

    best_intent = "general_query"
    best_score = 0
    for intent in INTENTS:
        score = scores.get(intent, 0)
        if score > best_score:
            best_intent = intent
            best_score = score

    return {
        "intent": best_intent if best_score > 0 else "general_query",
        "score": best_score if best_score > 0 else 0,
        "query": query,
    }


def get_context_sections(intent: str):
    return SECTION_MAP.get(intent, SECTION_MAP["general_query"])


def extract_parameters(query: str) -> dict:
    query_lower = query.lower()

    lambda_value = None
    theta_value = None

    lambda_patterns = [
        r"lambda\s+to\s+(\d+\.?\d*)",
        r"lambda\s*=\s*(\d+\.?\d*)",
        r"risk aversion\s+to\s+(\d+\.?\d*)",
    ]

    theta_patterns = [
        r"theta\s+to\s+(\d+\.?\d*)",
        r"theta_h\s*=\s*(\d+\.?\d*)",
        r"threshold\s+to\s+(\d+\.?\d*)",
    ]

    for pattern in lambda_patterns:
        match = re.search(pattern, query_lower)
        if match:
            lambda_value = float(match.group(1))
            break

    for pattern in theta_patterns:
        match = re.search(pattern, query_lower)
        if match:
            theta_value = float(match.group(1))
            break

    return {"lambda": lambda_value, "theta_H": theta_value}
