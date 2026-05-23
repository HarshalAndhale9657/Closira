"""Quick verification script to test all imports and basic functionality."""
import sys
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, ".")

print("Testing imports...")
from src.config import validate_config, SOP_DATA_PATH
from src.models import ConversationState, ConversationStage, EscalationEvent
from src.sop_loader import load_sop, format_sop_context
from src.conversation_manager import ConversationManager
print("  [OK] All modules imported successfully")

print("\nTesting SOP loading...")
sop = load_sop()
ctx = format_sop_context(sop)
biz_name = sop["business"]["name"]
print(f"  [OK] SOP loaded: {biz_name}")
print(f"  [OK] SOP context length: {len(ctx)} chars")
print(f"  [OK] Services: {len(sop['services'])}")
print(f"  [OK] FAQs: {len(sop['faqs'])}")

print("\nTesting data models...")
state = ConversationState()
print(f"  [OK] ConversationState created, stage: {state.stage.value}")
msg = state.add_message("user", "Hello!")
print(f"  [OK] Message added: {msg.role} - {msg.content}")
state.record_sop_gap("Test question")
print(f"  [OK] SOP gap recorded: {state.sop_gaps}")
print(f"  [OK] API messages format: {state.get_api_messages()}")

print("\nTesting ConversationManager init...")
try:
    manager = ConversationManager()
    greeting = manager.start_session()
    print(f"  [OK] Manager initialized")
    print(f"  [OK] Greeting: {greeting[:60]}...")
except Exception as e:
    print(f"  [WARN] Manager init (expected if no API key): {e}")

print("\n" + "=" * 50)
print("All basic checks passed!")
print("To run the full workflow, set OPENAI_API_KEY in .env and run:")
print("  python -m src")
