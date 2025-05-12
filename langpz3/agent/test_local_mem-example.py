#!/usr/bin/env python
import os
from pathlib import Path
from dotenv import load_dotenv
from workflow2 import app, WorkflowState
from langchain_core.messages import HumanMessage, AIMessage

def test_memory_persistence():
    """Test memory persistence with a sample user using workflow2.py"""
    
    # Load environment variables from .env file
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    
    # Verify OpenAI API key is loaded
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return
    print("✅ Environment variables loaded successfully")
    
    # Initialize state with user email
    state = WorkflowState(
        customer={"name": "Test User", "email": "test@example.com", "phoneNumber": "555-123-4567", "zipCode": "94105"},
        task={"description": "Test Task", "category": "Testing"},
        vendor={"name": "Test Vendor", "email": "vendor@example.com", "phoneNumber": "555-987-6543"},
        messages=[],
        sentiment="",
        reason="",
        current_step="validate",
        sentiment_attempts=0
    )
    
    # First interaction - positive sentiment
    print("\n=== First Interaction ===")
    state["messages"].append(AIMessage(content="Hello! I'm your AI concierge. How do you feel about starting the project?"))
    user_response = input("Enter your response: ")
    state["messages"].append(HumanMessage(content=user_response))
    result = app.invoke(state)
    
    # Second interaction - negative sentiment
    print("\n=== Second Interaction ===")
    user_response = input("Enter your response: ")
    state["messages"].append(HumanMessage(content=user_response))
    result = app.invoke(state)
    
    # Create new state to test persistence
    print("\n=== Testing Persistence ===")
    new_state = WorkflowState(
        customer={"name": "Test User", "email": "test@example.com", "phoneNumber": "555-123-4567", "zipCode": "94105"},
        task={"description": "Test Task", "category": "Testing"},
        vendor={"name": "Test Vendor", "email": "vendor@example.com", "phoneNumber": "555-987-6543"},
        messages=[],
        sentiment="",
        reason="",
        current_step="validate",
        sentiment_attempts=0
    )
    user_response = input("Enter your response: ")
    new_state["messages"].append(HumanMessage(content=user_response))
    result = app.invoke(new_state)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_memory_persistence() 