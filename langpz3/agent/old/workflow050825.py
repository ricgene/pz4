from typing import TypedDict, Dict, Any, List, Annotated
from langgraph.graph import StateGraph, END, START
import os
from langsmith.run_helpers import traceable
from datetime import datetime
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph import add_messages
from functools import lru_cache
import json

# Safe environment variable handling
try:
    from langchain_openai import ChatOpenAI
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: Required packages not available")

class WorkflowState(TypedDict):
    """Enhanced state management combining features from both implementations"""
    customer: dict  # Store customer information
    task: dict     # Store task details
    vendor: dict   # Store vendor information
    messages: Annotated[List[BaseMessage], add_messages]  # For conversation tracking
    current_step: Annotated[str, add_messages]  # For tracking workflow progress
    sentiment: str  # For tracking customer sentiment
    sentiment_attempts: int  # Track number of sentiment analysis attempts
    human_input_received: bool  # Flag to prevent recursion
    step_counts: dict  # Track recursion for each step
    skills_used: List[str]  # Track which skills have been used
    processed_inputs: List[str]  # Track processed inputs to prevent loops

@lru_cache(maxsize=1)
def get_llm():
    """Get the language model with error handling"""
    try:
        return ChatOpenAI(temperature=0, model="gpt-4")
    except Exception as e:
        print(f"Error initializing LLM: {str(e)}")
        return None

@traceable(project_name="enhanced-workflow")
def validate_input(state: WorkflowState) -> Dict:
    """Validate and initialize the workflow state with enhanced error handling"""
    print("\nValidating input...")
    validated_state = state.copy()
    
    # Initialize all required state fields with default values
    required_fields = {
        "customer": {"name": None, "email": None, "phone": None},
        "task": {"description": None, "status": "new", "category": None},
        "vendor": {"name": "Dave's Plumbing", "email": "dave@plumbing.com"},
        "messages": [],
        "sentiment": "neutral",
        "sentiment_attempts": 0,
        "step_counts": {
            "process_name": 0,
            "analyze_sentiment": 0,
            "confirm_end": 0,
            "process_additional": 0,
            "reschedule": 0,
            "human_step": 0
        },
        "human_input_received": False,
        "skills_used": [],
        "processed_inputs": []
    }
    
    # Initialize missing fields
    for field, default_value in required_fields.items():
        if field not in validated_state:
            validated_state[field] = default_value
        elif isinstance(default_value, dict):
            for subfield, subvalue in default_value.items():
                if subfield not in validated_state[field]:
                    validated_state[field][subfield] = subvalue
    
    print("Validation complete. Moving to initialize step...")
    return {"current_step": "initialize", **validated_state}

@traceable(project_name="enhanced-workflow")
def initialize_workflow(state: WorkflowState) -> Dict:
    """Initialize the workflow with a greeting and context awareness"""
    print("\nInitializing workflow...")
    
    # Add initialization to skills used
    if "initialize" not in state["skills_used"]:
        state["skills_used"].append("initialize")
    
    system_prompt = """You are a professional project coordinator helping customers with home improvement projects.
You're currently helping with a kitchen faucet installation project.
The vendor is Dave's Plumbing."""

    # If we have a saved name, ask about contractor meeting
    if state["customer"]["name"]:
        greeting = f"Hello {state['customer']['name']}! Have you had a chance to meet with Dave's Plumbing yet?"
    else:
        greeting = "Hello! I'm your project coordinator. I'll help you with your kitchen faucet installation. What's your name?"
    
    messages = [
        SystemMessage(content=system_prompt),
        AIMessage(content=greeting)
    ]
    
    print("Initialization complete. Moving to process_name step...")
    return {
        "messages": messages,
        "current_step": "process_name" if not state["customer"]["name"] else "check_contractor_meeting"
    }

@traceable(project_name="enhanced-workflow")
def process_name(state: WorkflowState) -> Dict:
    """Process the user's name with enhanced validation and error handling"""
    # Add to skills used
    if "process_name" not in state["skills_used"]:
        state["skills_used"].append("process_name")
    
    # Increment step counter
    state["step_counts"]["process_name"] = state["step_counts"].get("process_name", 0) + 1
    
    # Check recursion limit
    if state["step_counts"]["process_name"] > 5:
        state["messages"].append(AIMessage(content="I apologize, but I'm having trouble understanding. Please contact support for assistance."))
        return {"current_step": END}
    
    if not state.get("messages"):
        return {"current_step": "initialize"}
    
    last_message = state["messages"][-1]
    if not isinstance(last_message, HumanMessage):
        return {"current_step": "human_step"}
    
    name = last_message.content.strip()
    
    # If name is empty, ask again
    if not name:
        state["messages"].append(AIMessage(content="I didn't catch your name. Could you please tell me your name?"))
        return {"current_step": "human_step"}
    
    # Store the name in the customer dictionary
    state["customer"]["name"] = name
    
    # Add assistant's response acknowledging the name
    state["messages"].append(AIMessage(content=f"Thanks {name}! Would you like to schedule the kitchen faucet installation with Dave's Plumbing?"))
    
    return {"current_step": "analyze_sentiment"}

@traceable(project_name="enhanced-workflow")
def analyze_sentiment(state: WorkflowState) -> Dict:
    """Analyze customer sentiment with enhanced context awareness"""
    print("\nAnalyzing sentiment...")
    
    # Add to skills used
    if "analyze_sentiment" not in state["skills_used"]:
        state["skills_used"].append("analyze_sentiment")
    
    # Increment step counter
    state["step_counts"]["analyze_sentiment"] = state["step_counts"].get("analyze_sentiment", 0) + 1
    
    # Check recursion limit
    if state["step_counts"]["analyze_sentiment"] > 5:
        state["messages"].append(AIMessage(content="I apologize, but I'm having trouble understanding your response. Please contact support for assistance."))
        return {"current_step": END}
    
    if not state.get("messages"):
        print("No messages found, returning to process_name")
        return {"current_step": "process_name"}
    
    # Find the last human message
    last_message = None
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            last_message = msg
            break
    
    if not last_message:
        print("No human message found, returning to human_step")
        return {"current_step": "human_step"}
    
    content = last_message.content.lower()
    
    # Check for positive sentiment
    if any(word in content for word in ["yes", "yeah", "sure", "okay", "definitely", "absolutely"]):
        state["sentiment"] = "positive"
        state["messages"].append(AIMessage(content="Great! I'll have Dave's Plumbing contact you to confirm the details. Is there anything else you'd like to know?"))
        return {"current_step": "confirm_end"}
    
    # Check for negative sentiment
    if any(word in content for word in ["no", "nope", "not", "don't", "cannot", "cant", "reschedule"]):
        state["sentiment"] = "negative"
        return {"current_step": "reschedule"}
    
    # Unclear sentiment
    state["sentiment"] = "unclear"
    state["messages"].append(AIMessage(content="I'm not sure if you want to schedule the installation. Could you please answer with a clear yes or no?"))
    return {"current_step": "human_step"}

@traceable(project_name="enhanced-workflow")
def human_step(state: WorkflowState) -> Dict:
    """Enhanced human interaction handling with better state management"""
    # Add to skills used
    if "human_step" not in state["skills_used"]:
        state["skills_used"].append("human_step")
    
    # Increment step counter
    state["step_counts"]["human_step"] = state["step_counts"].get("human_step", 0) + 1
    
    # Check recursion limit
    if state["step_counts"]["human_step"] > 5:
        state["messages"].append(AIMessage(content="I apologize, but I'm having trouble understanding. Please contact support for assistance."))
        return {"current_step": END}
    
    # Check if we have a human message as the last message
    if state.get("messages") and len(state["messages"]) > 0:
        last_message = state["messages"][-1]
        if isinstance(last_message, HumanMessage):
            # Check if we've already processed this input
            if last_message.content in state["processed_inputs"]:
                state["messages"].append(AIMessage(content="I've already processed that input. Could you please provide new information?"))
                return {"current_step": "human_step"}
            
            # Add to processed inputs
            state["processed_inputs"].append(last_message.content)
            
            # We have received human input, so process it
            state["human_input_received"] = True
            content = last_message.content.lower()
            
            # Check for end conversation
            if content in ["end", "bye", "goodbye", "exit", "quit"]:
                state["messages"].append(AIMessage(content="Thank you for your time! Have a great day!"))
                return {"current_step": END}
            
            # Check for reschedule
            if "reschedule" in content:
                return {"current_step": "reschedule"}
            
            # Check for additional questions
            if "?" in content:
                return {"current_step": "process_additional"}
            
            # If no name yet, go to process_name
            if not state["customer"].get("name"):
                return {"current_step": "process_name"}
            
            # Default to analyzing sentiment
            return {"current_step": "analyze_sentiment"}
    
    # No human input received or no messages, stay in human_step
    state["human_input_received"] = False
    return {"current_step": "human_step"}

def create_workflow() -> StateGraph:
    """Create the enhanced workflow graph with better error handling and state management"""
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("validate", validate_input)
    workflow.add_node("initialize", initialize_workflow)
    workflow.add_node("process_name", process_name)
    workflow.add_node("analyze_sentiment", analyze_sentiment)
    workflow.add_node("human_step", human_step)
    
    # Add edges with clear flow control
    workflow.add_edge(START, "validate")
    workflow.add_edge("validate", "initialize")
    workflow.add_edge("initialize", "process_name")
    workflow.add_edge("initialize", "human_step")
    
    # From human_step, conditionally go to next step based on state
    workflow.add_conditional_edges(
        "human_step",
        lambda state: state.get("current_step", "human_step"),
        {
            "process_name": "process_name",
            "analyze_sentiment": "analyze_sentiment",
            "human_step": "human_step",
            END: END
        }
    )
    
    # From process_name, go to analyze_sentiment or human_step
    workflow.add_conditional_edges(
        "process_name",
        lambda state: state.get("current_step", "human_step"),
        {
            "analyze_sentiment": "analyze_sentiment",
            "human_step": "human_step",
            END: END
        }
    )
    
    # From analyze_sentiment, go to human_step or end
    workflow.add_conditional_edges(
        "analyze_sentiment",
        lambda state: state.get("current_step", "human_step"),
        {
            "human_step": "human_step",
            END: END
        }
    )
    
    # Set recursion limit
    workflow.recursion_limit = 5
    
    return workflow.compile()

def save_customer_name(name: str, filename: str = "customer.json") -> None:
    """Save the customer name to a JSON file."""
    with open(filename, "w") as f:
        json.dump({"name": name}, f, indent=2)

def load_customer_name(filename: str = "customer.json") -> str:
    """Load customer name from a JSON file."""
    if not os.path.exists(filename):
        return None
    
    with open(filename, "r") as f:
        data = json.load(f)
        return data.get("name")

def main():
    """Run the enhanced workflow."""
    print("\nStarting enhanced workflow...")
    
    # Try to load existing customer name
    saved_name = load_customer_name()
    
    # Initialize state with all required fields
    state = {
        "customer": {"name": saved_name},
        "task": {
            "description": "Kitchen faucet installation",
            "status": "new",
            "category": "plumbing"
        },
        "vendor": {
            "name": "Dave's Plumbing",
            "email": "dave@plumbing.com"
        },
        "messages": [],
        "sentiment": "neutral",
        "sentiment_attempts": 0,
        "step_counts": {},
        "human_input_received": False,
        "skills_used": [],
        "processed_inputs": []
    }
    
    # Create and run the workflow
    workflow = create_workflow()
    
    try:
        result = workflow.invoke(state)
        
        # Print agent's responses
        for message in result["messages"]:
            if isinstance(message, AIMessage):
                print(f"Agent: {message.content}")
        
        # Save customer name if it's been updated
        if result["customer"]["name"] != saved_name:
            save_customer_name(result["customer"]["name"])
            
    except Exception as e:
        print(f"Error running workflow: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 