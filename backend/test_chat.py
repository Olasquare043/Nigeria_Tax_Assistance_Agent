# test_chat_integration.py
import sys
import os
from pathlib import Path

# Add project root to path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print("🧪 Testing Chat Integration with AI Agent...")

# Import from chat.py
try:
    from chat import AIClient
    print("✅ AIClient imported successfully")
    
    # Test 1: Simple test without conversation history
    print("\n1. Testing AI response without history...")
    test_session_id = "test_session_123"
    test_message = "What are the VAT changes in the 2024 tax reform?"
    
    response = AIClient.get_response(test_session_id, test_message)
    
    print(f"   Response received: {response.get('answer', 'No answer')[:100]}...")
    print(f"   Route: {response.get('route', 'unknown')}")
    print(f"   Citations: {len(response.get('citations', []))}")
    print(f"   Refusal: {response.get('refusal', False)}")
    
    # Test 2: Check if it's using fallback
    if response.get('route') == 'fallback':
        print("   ⚠️ Using fallback response - AI agent may not be working properly")
    else:
        print("   ✅ Using AI agent response")
    
    # Test 3: Test with conversation history
    print("\n2. Testing AI response with conversation history...")
    conversation_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi! How can I help you with Nigerian tax reform?"},
        {"role": "user", "content": "I want to know about VAT"}
    ]
    
    response2 = AIClient.get_response(
        test_session_id, 
        "What's the new VAT rate?", 
        conversation_history
    )
    
    print(f"   Response received: {response2.get('answer', 'No answer')[:100]}...")
    print(f"   Route: {response2.get('route', 'unknown')}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test completed")