# test_agent.py
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_engine.tax_engine.agent_graph import build_graph
from langchain_core.messages import HumanMessage

# Build the graph
graph = build_graph()

# Test with a simple message
test_state = {
    "messages": [HumanMessage(content="What are the VAT changes?")]
}

result = graph.invoke(
    test_state,
    config={"configurable": {"thread_id": "test_thread"}}
)

print("Test result:", result)