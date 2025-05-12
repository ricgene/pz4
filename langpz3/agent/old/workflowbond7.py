# Implementation of workflowbond7.py with API intent detection and recursion fixes

from typing import TypedDict, Dict, Any, List, Annotated, Literal
from langgraph.graph import StateGraph, END
import os
from langsmith.run_helpers import traceable
import json
from datetime import datetime
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph import add_messages
from functools import lru_cache
import sys

# Safe environment variable handling
try:
    from langchain_openai import ChatOpenAI
    import openai
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables
    print("Environment variables loaded")
    print(f"OPENAI_API_KEY present: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
except ImportError:
    print("Warning: langchain_openai or openai not available")

# Enhanced State Definition for 007 Productivity Agent
class AgentState(TypedDict):
    user: dict  # Store user information (name, preferences)
    todos: list  # Store todo items
    messages: Annotated[List[BaseMessage], add_messages]  # For conversation tracking
    current_step: str  # For tracking workflow progress
    skills_used: list  # Track which skills were used in the session
    processed_inputs: list  # Track processed inputs to avoid loops

# Initialize Models with error handling
@lru_cache(maxsize=4)
def _get_model(model_name: str):
    """Get a model with the specified name"""
    try:
        if model_name == "openai":
            model = ChatOpenAI(temperature=0, model_name="gpt-4o")
            return model
        else:
            raise ValueError(f"Unsupported model type: {model_name}")
    except Exception as e:
        print(f"Error initializing model: {str(e)}")
        # Return a mock model if initialization fails
        return None

# Node Implementations
@traceable(project_name="007-productivity-agent")
def validate_input(state: AgentState):
    """Validate the input state and initialize if needed"""
    
    # Initialize workflow tracking fields if not present
    if "user" not in state:
        state["user"] = {"name": None}
    if "todos" not in state:
        state["todos"] = []
    if "current_step" not in state:
        state["current_step"] = "initialize_agent"
    if "messages" not in state:
        state["messages"] = []
    if "skills_used" not in state:
        state["skills_used"] = []
    if "processed_inputs" not in state:
        state["processed_inputs"] = []  # Track processed inputs
        
    return state

@traceable(project_name="007-productivity-agent")
def initialize_agent(state: AgentState):
    """Initialize the agent state"""
    # Just update the current step
    return {
        "current_step": "generate_greeting"
    }

@traceable(project_name="007-productivity-agent")
def generate_greeting(state: AgentState):
    """Generate the initial greeting for the user"""
    
    # Check if we know the user's name
    user_name = state["user"].get("name")
    
    # Construct the greeting message
    if user_name:
        greeting = f"Hello {user_name}! I'm 007, your personal productivity agent. How can I help you with your kitchen faucet installation today?"
    else:
        greeting = "Hello! I'm 007, your personal productivity agent. I don't think we've met before. What's your name?"
    
    # Add the greeting as a system message
    system_prompt = """You are 007, a personal productivity agent.
You help users manage their projects and connect with vendors.
For this conversation, we're focusing on a kitchen faucet installation project.
The vendor is Dave's Plumbing."""
    
    # Add the messages
    messages = [
        SystemMessage(content=system_prompt),
        AIMessage(content=greeting)
    ]
    
    return {
        "messages": messages,
        "current_step": "process_input"
    }

@traceable(project_name="007-productivity-agent")
def process_input(state: AgentState):
    """Process user input and determine next action"""
    
    # Get the latest message from the user
    if not state["messages"] or len(state["messages"]) == 0:
        return {
            "current_step": "end_session"
        }
        
    latest_message = state["messages"][-1]
    
    # Skip if not a human message
    if not isinstance(latest_message, HumanMessage):
        return {
            "current_step": "general_question"
        }
    
    # If we're still in the introduction phase and don't know the user's name
    if state["user"].get("name") is None:
        # Extract name from message
        name = latest_message.content.strip()
        if len(name) > 0:
            # Update user info and propose contacting vendor
            return {
                "user": {"name": name},
                "messages": [AIMessage(content=f"Nice to meet you, {name}! For your kitchen faucet installation, we have an excellent vendor, Dave's Plumbing. Would you like to contact them tomorrow?")],
                "current_step": "process_input"
            }
    
    # Otherwise, analyze sentiment about contacting the vendor
    model = _get_model("openai")
    if not model:
        return {
            "messages": [AIMessage(content="I'm sorry, but I'm having trouble processing your request right now. Please try again later.")],
            "current_step": "end_session"
        }
    
    # Analyze sentiment
    system_prompt = """Analyze the user's response to determine if they want to contact Dave's Plumbing.
Categories:
- positive: User agrees to contact the vendor
- negative: User does not want to contact the vendor
- unknown: Cannot determine user's preference

Format your response as a JSON object with two fields:
- "sentiment": One of the categories above
- "reason": Brief explanation of the sentiment

Example:
{"sentiment": "positive", "reason": "User agreed to contact vendor"}"""
    
    try:
        messages_for_sentiment = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=latest_message.content)
        ]
        sentiment_response = model.invoke(messages_for_sentiment)
        
        try:
            sentiment_data = json.loads(sentiment_response.content)
            sentiment = sentiment_data.get("sentiment", "unknown")
            
            if sentiment == "positive":
                return {
                    "current_step": "end_conversation",
                    "messages": [AIMessage(content=f"Thank you {state['user']['name']}, have a great day!")]
                }
            else:  # For both negative and unknown
                return {
                    "current_step": "end_conversation",
                    "messages": [AIMessage(content=f"I understand, {state['user']['name']}. Would you like me to contact Dave's Plumbing for you instead?")]
                }
        except json.JSONDecodeError:
            return {
                "current_step": "end_conversation",
                "messages": [AIMessage(content=f"I understand, {state['user']['name']}. Would you like me to contact Dave's Plumbing for you instead?")]
            }
    except Exception as e:
        print(f"Error in sentiment analysis: {str(e)}")
        return {
            "current_step": "end_conversation",
            "messages": [AIMessage(content=f"I apologize {state['user']['name']}, but I'm having trouble understanding. Would you like me to contact Dave's Plumbing for you instead?")]
        }

@traceable(project_name="007-productivity-agent")
def end_conversation(state: AgentState):
    """End the conversation"""
    return {
        "current_step": END
    }

@traceable(project_name="007-productivity-agent")
def end_session(state: AgentState):
    """End session due to error or other issue"""
    return {
        "current_step": END
    }

# Define the workflow graph
def create_agent_graph():
    """Create the workflow graph"""
    # Create a new graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("validate_input", validate_input)
    workflow.add_node("initialize_agent", initialize_agent)
    workflow.add_node("generate_greeting", generate_greeting)
    workflow.add_node("process_input", process_input)
    workflow.add_node("end_conversation", end_conversation)
    workflow.add_node("end_session", end_session)
    
    # Define edges
    workflow.add_edge("validate_input", "initialize_agent")
    workflow.add_edge("initialize_agent", "generate_greeting")
    workflow.add_edge("generate_greeting", "process_input")
    workflow.add_edge("process_input", "process_input")  # Allow multiple turns
    workflow.add_edge("end_conversation", END)
    workflow.add_edge("end_session", END)
    
    # Set entry point
    workflow.set_entry_point("validate_input")
    
    return workflow

# Create the compiled application
app = create_agent_graph().compile(recursion_limit=5)

# Main function for local testing
def main():
    """Run the agent workflow for local testing"""
    
    workflow = create_agent_graph().compile(recursion_limit=5)
    
    # Initial empty state
    state = {"messages": []}
    
    # Print welcome
    print("\n=== 007 Productivity Agent ===\n")
    print("Type 'exit' to end the conversation.\n")
    
    # Get initial response from agent
    try:
        result = workflow.invoke(state)
        
        # Print agent's greeting
        for message in result["messages"]:
            if isinstance(message, AIMessage):
                print(f"Agent: {message.content}")
        
        # Main conversation loop
        while True:
            # Get user input
            user_input = input("\nYou: ")
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\nExiting conversation. Goodbye!")
                break
            
            # Add user message to state
            state = result.copy()
            state["messages"].append(HumanMessage(content=user_input))
            
            # Invoke workflow
            try:
                result = workflow.invoke(state)
                
                # Print agent's response
                for message in result["messages"]:
                    if isinstance(message, AIMessage):
                        print(f"Agent: {message.content}")
                
                # Check if workflow ended
                if result["current_step"] == END:
                    break
            except Exception as e:
                print(f"\nError processing your request: {str(e)}")
                print("Let's try again.")
    except Exception as e:
        print(f"\n❌ Error running agent: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()