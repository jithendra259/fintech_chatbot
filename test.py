

from orchestrator.intent_classifier import (
    classify_intent,
    get_context_sections,
    extract_parameters
)

tests = [
    "What is the current regime?",
    "Show me the portfolio weights",
    "What is the Sharpe ratio?",
    "Compare optimized vs equal weight",
    "What is the instability index?",
    "Change lambda to 1",
    "Change theta to 0.5",
    "What happened in the training period?",
    "Hello how are you"
]

for q in tests:
    result = classify_intent(q)
    sections = get_context_sections(result["intent"])
    params = extract_parameters(q)
    print(f"Query: {q}")
    print(f"  Intent:   {result['intent']} (score: {result['score']})")
    print(f"  Sections: {sections}")
    if params["lambda"] or params["theta_H"]:
        print(f"  Params:   {params}")
    print()