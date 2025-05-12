#!/usr/bin/env python
import argparse
import os
import sys
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage

# Import the agent state graph from 007-workflow.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    # Try to import from current directory first
    from agent.workflowbond7_openai import AgentState, validate_input, initialize_agent, generate_greeting
    print("Imported from agent directory")
except ImportError:
    try:
        # If running from agent directory, import directly
        from workflowbond7_openai import AgentState, validate_input, initialize_agent, generate_greeting
        print("Imported directly")
    except ImportError:
        print("Error: Could not import workflowbond7_openai. Make sure you're running from the correct directory.")
        sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(description="Run the 007 Productivity Agent")
    parser.add_argument("--mocked", action="store_true", 
                        help="Run with mocked models instead of real API calls")
    return parser.parse_args()

def run_agent():
    """Run the 007 agent interactively"""
    # Initialize state
    state = validate_input({})
    state = {**state, **initialize_agent(state)}
    state = {**state, **generate_greeting(state)}
    
    # Print the initial greeting
    messages = state.get("messages", [])
    if messages:
        for message in messages:
            if message.type == "ai":
                print(f"Agent: {message.content}")
    
    # Interactive loop
    while True:
        # Get user input
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Agent: Goodbye!")
                break
            
            # Add user input to messages
            state["messages"].append(HumanMessage(content=user_input))
            
            # Check if we have a process_input function in the imported module
            if 'process_input' in globals():
                print("🔄 Calling process_input function...")
                try:
                    # Call the existing process_input function
                    updated_state = process_input(state)
                    state = {**state, **updated_state}
                    
                    # Display the agent's response
                    messages = state.get("messages", [])
                    if messages:
                        for message in messages[-1:]:  # Just the last message
                            if message.type == "ai":
                                print(f"Agent: {message.content}")
                except Exception as e:
                    print(f"❌ Error in process_input: {str(e)}")
            else:
                # Simple mock implementation if process_input doesn't exist
                print("📝 Using built-in process_input logic (no function found in module)")
                
                # Check for name introduction
                if "my name is" in user_input.lower() or state["messages"][-2].content.lower().endswith("what's your name?"):
                    # Extract name or use the input as name
                    name_parts = user_input.split("my name is ")
                    if len(name_parts) > 1:
                        name = name_parts[1].strip()
                    else:
                        name = user_input.strip()
                    
                    # Update state with user name
                    state["user"]["name"] = name
                    print(f"📊 Updated user name to: {name}")
                    
                    # Create response
                    response = f"Nice to meet you, {name}! How can I help you today? I can help you manage tasks, find information, or assist with your productivity needs."
                else:
                    # Generic response for other inputs
                    response = "I understand. Is there anything specific you'd like help with today? I can help manage your tasks or find information for you."
                
                # Add AI response to messages
                from langchain_core.messages import AIMessage
                state["messages"].append(AIMessage(content=response))
                print(f"Agent: {response}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    args = parse_args()
    
    # Set the environment variable based on the flag
    if args.mocked:
        os.environ["MOCK_MODE"] = "True"
        print("🚀 Starting 007 Productivity Agent with Mocked Implementation")
        print("=== 007 Productivity Agent (Mocked Mode) ===")
        print("Using predefined inputs for testing. Type your own inputs when mocked inputs run out.")
    else:
        os.environ["MOCK_MODE"] = "False"
        print("🚀 Starting 007 Productivity Agent with OpenAI Integration")
        print("=== 007 Productivity Agent (Live Mode) ===")
        print("Using real OpenAI API for all model calls.")
    
    # Run the agent
    run_agent()