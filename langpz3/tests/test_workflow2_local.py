import sys
import os
import pickle

# Add the 'agent' directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agent'))

# Import the cloud version of workflow2
from workflow2_cloud import (
    WorkflowState,
    validate_input,
    initialize_state,
    generate_initial_prompt,
    analyze_sentiment,
    process_sentiment,
    process_data,
    format_output
)
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import json

MEMORY_DIR = os.path.join(os.path.dirname(__file__), '..', 'agent', 'memory')

def get_memory_path(user_id):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    return os.path.join(MEMORY_DIR, f"{user_id}_name.pkl")

def load_user_name(user_id):
    path = get_memory_path(user_id)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None

def save_user_name(user_id, name):
    path = get_memory_path(user_id)
    with open(path, "wb") as f:
        pickle.dump(name, f)

def create_initial_state():
    """Create an initial state for testing"""
    return {
        "customer": {
            "name": "Test User",
            "email": "test@example.com",
            "phoneNumber": "555-0123",
            "zipCode": "12345"
        },
        "task": {
            "description": "Kitchen renovation",
            "category": "Home Improvement"
        },
        "vendor": {
            "name": "Dave's Plumbing",
            "email": "dave@plumbing.com",
            "phoneNumber": "555-9876"
        },
        "messages": [],
        "sentiment": "",
        "reason": "",
        "current_step": "validate",
        "sentiment_attempts": 0,
        "summary": ""
    }

def print_messages(messages):
    """Print messages in a readable format"""
    for msg in messages:
        if isinstance(msg, SystemMessage):
            print("\nSystem:", msg.content)
        elif isinstance(msg, HumanMessage):
            print("\nYou:", msg.content)
        elif isinstance(msg, AIMessage):
            print("\nAssistant:", msg.content)

def update_state(current_state, new_state):
    """Merge new state updates with current state"""
    if isinstance(new_state, dict):
        return {**current_state, **new_state}
    return current_state

def main():
    print("\nStarting workflow2 cloud test...")
    print("Initializing workflow with test data...")
    
    # Create initial state
    state = create_initial_state()
    
    try:
        # Run through initial steps
        state = update_state(state, validate_input(state))
        state = update_state(state, initialize_state(state))
        state = update_state(state, generate_initial_prompt(state))
        
        # Print initial messages
        print("\nInitial conversation:")
        print_messages(state["messages"])
        
        # Main conversation loop
        while True:
            # Get user input
            user_input = input("\nYour response (or 'quit' to end): ")
            
            if user_input.lower() == 'quit':
                print("\nEnding conversation...")
                break
            
            # Add user message to state
            state["messages"].append(HumanMessage(content=user_input))
            
            # Process the conversation
            state = update_state(state, analyze_sentiment(state))
            state = update_state(state, process_sentiment(state))
            state = update_state(state, process_data(state))
            state = update_state(state, format_output(state))
            
            # Print the conversation
            print("\nUpdated conversation:")
            print_messages(state["messages"])
            
            # Check if we should end
            if state.get("current_step") == "end":
                print("\nWorkflow completed!")
                break
                
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 