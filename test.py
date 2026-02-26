from config.config import config
from orchestrator.orchestrator import Orchestrator

orc = Orchestrator(config)
result = orc.start_session(["AAPL", "MSFT", "GOOGL"])
print("Session:", result["message"])
print()

print("Test 4 - Change theta to 0.5:")
r = orc.chat("Change theta to 0.5")
print("Response:", r["response"])
print()

print("Test 5 - Change theta back to 1.0:")
r = orc.chat("Change theta to 1.0")
print("Response:", r["response"])