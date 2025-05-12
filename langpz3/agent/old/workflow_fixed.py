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
    customer: dict  # Store customer information
    task: dict     # Store task details
    vendor: dict   # Store vendor information
    messages: Annotated[List[BaseMessage], add_messages]  # For conversation tracking
    current_step: Annotated[str, add_messages]  # For tracking workflow progress
    sentiment: str  # For tracking customer sentiment
    sentiment_attempts: int  # Track number of sentiment analysis attempts
    human_input_received: bool  # Flag to prevent recursion

@lru_cache(maxsize=1)
def get_llm():
    """Get the language model with error handling"""
    try:
        return ChatOpenAI(temperature=0, model="gpt-4")
    except Exception as e:
        print(f"Error initializing LLM: {str(e)}")
        return None

def validate_input(state: WorkflowState) -> Dict:
    """Validate and initialize the workflow state"""
    print("\nValidating input...")
    validated_state = state.copy()
    
    # Initialize all required state fields
    if "customer" not in validated_state:
        validated_state["customer"] = {"name": None}
    if "task" not in validated_state:
        validated_state["task"] = {"description": None, "status": "new"}
    if "vendor" not in validated_state:
        validated_state["vendor"] = {"name": "Dave's Plumbing", "email": "dave@plumbing.com"}
    if "messages" not in validated_state:
        validated_state["messages"] = []
    if "sentiment" not in validated_state:
        validated_state["sentiment"] = "neutral"
    if "sentiment_attempts" not in validated_state:
        validated_state["sentiment_attempts"] = 0
    if "step_counts" not in validated_state:
        validated_state["step_counts"] = {
            "process_name": 0,
            "analyze_sentiment": 0,
            "confirm_end": 0,
            "process_additional": 0,
            "reschedule": 0
        }
    if "human_input_received" not in validated_state:
        validated_state["human_input_received"] = False
        
    print("Validation complete. Moving to initialize step...")
    return {"current_step": "initialize", **validated_state}

def initialize_workflow(state: WorkflowState) -> Dict:
    """Initialize the workflow with a greeting."""
    print("\nInitializing workflow...")
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

def process_name(state: WorkflowState) -> Dict:
    """Process the user's name and update the conversation flow."""
    # Initialize step_counts if not present
    if "step_counts" not in state:
        state["step_counts"] = {
            "process_name": 0,
            "analyze_sentiment": 0,
            "confirm_end": 0,
            "process_additional": 0,
            "reschedule": 0
        }
    
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

def process_schedule(state: WorkflowState) -> Dict:
    """Process the user's scheduling response."""
    if not state.get("messages"):
        return {"current_step": "initialize"}
    
    last_message = state["messages"][-1]
    if not isinstance(last_message, HumanMessage):
        return {"current_step": "human_step"}
    
    # After getting their scheduling preference, thank them and end
    response = "Thank you for letting me know. I'll have Dave's Plumbing contact you to confirm the details. Have a great day!"
    
    state["messages"].append(AIMessage(content=response))
    
    return {
        "current_step": END,
        "messages": state["messages"]
    }

def confirm_end(state: WorkflowState) -> Dict:
    """Confirm if the user wants to end the conversation"""
    # Initialize step_counts if not present
    if "step_counts" not in state:
        state["step_counts"] = {
            "process_name": 0,
            "analyze_sentiment": 0,
            "confirm_end": 0,
            "process_additional": 0,
            "reschedule": 0
        }
    
    # Increment step counter
    state["step_counts"]["confirm_end"] = state["step_counts"].get("confirm_end", 0) + 1
    
    # Check recursion limit
    if state["step_counts"]["confirm_end"] > 5:
        state["messages"].append(AIMessage(content="I apologize, but I'm having trouble understanding. Please contact support for assistance."))
        return {"current_step": END}
    
    if not state.get("messages"):
        return {"current_step": "process_name"}
    
    last_message = state["messages"][-1]
    if not isinstance(last_message, HumanMessage):
        return {"current_step": "human_step"}
    
    content = last_message.content.lower().strip()
    
    # If empty message or goodbye, end conversation
    if not content or any(word in content for word in ["bye", "goodbye", "end", "done", "finished", "no"]):
        state["messages"].append(AIMessage(content="Thank you for your time! Have a great day!"))
        return {"current_step": END}
    
    # If there's a question mark, process additional questions
    if "?" in content:
        return {"current_step": "process_additional"}
    
    # For any other response, ask if they have questions
    state["messages"].append(AIMessage(content="Is there anything specific you'd like to know about the installation?"))
    return {"current_step": "human_step"}

def process_additional(state: WorkflowState) -> Dict:
    """Process additional questions or requests"""
    # Initialize step_counts if not present
    if "step_counts" not in state:
        state["step_counts"] = {
            "process_name": 0,
            "analyze_sentiment": 0,
            "confirm_end": 0,
            "process_additional": 0,
            "reschedule": 0
        }
    
    # Increment step counter
    state["step_counts"]["process_additional"] = state["step_counts"].get("process_additional", 0) + 1
    
    # Check recursion limit
    if state["step_counts"]["process_additional"] > 5:
        state["messages"].append(AIMessage(content="I apologize, but I'm having trouble understanding. Please contact support for assistance."))
        return {"current_step": END}
    
    if not state.get("messages"):
        return {"current_step": "process_name"}
    
    last_message = state["messages"][-1]
    if not isinstance(last_message, HumanMessage):
        return {"current_step": "human_step"}
    
    # Add a generic response about contacting the plumber
    state["messages"].append(AIMessage(content="Dave's Plumbing will be able to provide detailed information about your specific requirements when they contact you. Is there anything else you'd like to know?"))
    
    return {"current_step": "confirm_end"}

def analyze_sentiment(state: WorkflowState) -> Dict:
    """Analyze customer sentiment about scheduling"""
    print("\nAnalyzing sentiment...")
    
    # Initialize step_counts if not present
    if "step_counts" not in state:
        state["step_counts"] = {
            "process_name": 0,
            "analyze_sentiment": 0,
            "confirm_end": 0,
            "process_additional": 0,
            "reschedule": 0
        }
    
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

def reschedule(state: WorkflowState) -> Dict:
    """Handle rescheduling requests"""
    # Initialize step_counts if not present
    if "step_counts" not in state:
        state["step_counts"] = {
            "process_name": 0,
            "analyze_sentiment": 0,
            "confirm_end": 0,
            "process_additional": 0,
            "reschedule": 0
        }
    
    # Increment step counter
    state["step_counts"]["reschedule"] = state["step_counts"].get("reschedule", 0) + 1
    
    # Check recursion limit
    if state["step_counts"]["reschedule"] > 5:
        state["messages"].append(AIMessage(content="I apologize, but I'm having trouble understanding. Please contact support for assistance."))
        return {"current_step": END}
    
    if not state.get("messages"):
        return {"current_step": "process_name"}
    
    last_message = state["messages"][-1]
    if not isinstance(last_message, HumanMessage):
        state["messages"].append(AIMessage(content="I understand you'd like to reschedule. When would be a better time for you?"))
        return {"current_step": "human_step"}
    
    # Process the rescheduling request
    state["messages"].append(AIMessage(content="I'll note your preferred time and have Dave's Plumbing contact you to confirm the new schedule. Is there anything else you'd like to know?"))
    
    return {"current_step": "confirm_end"}

def process_notes(state: WorkflowState) -> Dict:
    """Process any specific notes about the installation."""
    if not state.get("messages"):
        return {"current_step": "initialize"}
    
    last_message = state["messages"][-1]
    if not isinstance(last_message, HumanMessage):
        return {"current_step": "human_step"}
    
    # Store the notes (you could add them to a task dict if needed)
    notes = last_message.content
    
    response = "Thank you for providing those details. I've noted them for the installation team. "
    response += "That concludes our conversation. Dave's Plumbing will be in touch soon to schedule your installation. "
    response += "Have a great day!"
    
    state["messages"].append(AIMessage(content=response))
    
    return {
        "current_step": "end",
        "messages": state["messages"]
    }

def human_step(state: WorkflowState) -> Dict:
    """Process human input and determine next step"""
    # Initialize step_counts if not present
    if "step_counts" not in state:
        state["step_counts"] = {
            "process_name": 0,
            "analyze_sentiment": 0,
            "confirm_end": 0,
            "process_additional": 0,
            "reschedule": 0
        }
    
    # Check if we have a human message as the last message
    if state.get("messages") and len(state["messages"]) > 0:
        last_message = state["messages"][-1]
        if isinstance(last_message, HumanMessage):
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
    
    # No human input received, stay in this state
    state["human_input_received"] = False
    return {"current_step": END}

def check_contractor_meeting(state: WorkflowState) -> Dict:
    """Check if the customer has met with the contractor."""
    if not state.get("messages"):
        return {"current_step": "initialize"}
    
    last_message = state["messages"][-1]
    if not isinstance(last_message, HumanMessage):
        return {"current_step": "human_step"}
    
    response = last_message.content.strip().lower()
    
    # Add appropriate response based on their answer
    if "yes" in response or "yeah" in response:
        state["messages"].append(AIMessage(content="Great! I'm glad the meeting went well. Is there anything else you need help with?"))
    else:
        state["messages"].append(AIMessage(content="No problem! Dave's Plumbing will contact you to schedule a meeting. Is there anything else you need help with?"))
    
    return {
        "current_step": "confirm_end",
        "messages": state["messages"]
    }

def create_workflow() -> StateGraph:
    """Create the workflow graph"""
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("validate", validate_input)
    workflow.add_node("initialize", initialize_workflow)
    workflow.add_node("process_name", process_name)
    workflow.add_node("analyze_sentiment", analyze_sentiment)
    workflow.add_node("confirm_end", confirm_end)
    workflow.add_node("process_additional", process_additional)
    workflow.add_node("human_step", human_step)
    workflow.add_node("reschedule", reschedule)
    
    # Add edges with clear flow control
    workflow.add_edge(START, "validate")
    workflow.add_edge("validate", "initialize")
    workflow.add_edge("initialize", "human_step")
    
    # From human_step, conditionally go to next step if human input is received
    workflow.add_conditional_edges(
        "human_step",
        lambda state: state["current_step"],
        {
            "process_name": "process_name",
            "analyze_sentiment": "analyze_sentiment",
            "process_additional": "process_additional",
            "reschedule": "reschedule",
            END: END
        }
    )
    
    # From process_name, go to human_step
    workflow.add_edge("process_name", "human_step")
    
    # From analyze_sentiment, conditionally go to next step
    workflow.add_conditional_edges(
        "analyze_sentiment",
        lambda state: state["current_step"],
        {
            "confirm_end": "confirm_end",
            "reschedule": "reschedule",
            "human_step": "human_step",
            END: END
        }
    )
    
    # From confirm_end, conditionally go to next step
    workflow.add_conditional_edges(
        "confirm_end",
        lambda state: state["current_step"],
        {
            "process_additional": "process_additional",
            "human_step": "human_step",
            END: END
        }
    )
    
    # From process_additional, go to confirm_end
    workflow.add_edge("process_additional", "confirm_end")
    
    # From reschedule, go to confirm_end
    workflow.add_edge("reschedule", "confirm_end")
    
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
    """Run the workflow."""
    print("\nStarting workflow...")
    
    # Try to load existing customer name
    saved_name = load_customer_name()
    
    # Initialize state
    state = {
        "customer": {"name": saved_name},
        "task": {
            "description": "Kitchen faucet installation",
            "schedule": None
        },
        "vendor": {
            "name": "Dave's Plumbing",
            "email": "dave@plumbing.com"
        },
        "messages": [],
        "sentiment": "neutral",
        "sentiment_attempts": 0,
        "step_counts": {},
        "human_input_received": False
    }
    
    # Define the workflow graph
    workflow = {
        "validate": validate_input,
        "initialize": initialize_workflow,
        "process_name": process_name,
        "process_schedule": process_schedule,
        "confirm_end": confirm_end,
        "process_additional": process_additional,
        "analyze_sentiment": analyze_sentiment,
        "reschedule": reschedule,
        "process_notes": process_notes,
        "human_step": human_step,
        "check_contractor_meeting": check_contractor_meeting
    }
    
    current_step = "validate"
    
    while current_step != "__end__":
        print(f"\nCurrent step: {current_step}")
        
        if current_step not in workflow:
            print(f"Error: Invalid step '{current_step}'")
            break
            
        try:
            # Execute the current step
            step_output = workflow[current_step](state)
            print(f"\nStep output: {step_output}")
            
            # Update state with step output
            for key, value in step_output.items():
                if key != "current_step":  # Don't update current_step here
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if subkey in state:
                                if isinstance(state[subkey], list) and isinstance(subvalue, list):
                                    state[subkey].extend(subvalue)
                                elif isinstance(state[subkey], dict) and isinstance(subvalue, dict):
                                    state[subkey].update(subvalue)
                                else:
                                    state[subkey] = subvalue
                    else:
                        state[key] = value
            
            # Update current step
            if "current_step" in step_output:
                current_step = step_output["current_step"]
            
            # Print current messages for debugging
            print(f"\nCurrent messages: {[msg.content for msg in state['messages']]}")
            
            # Save customer name if it's been updated
            if state["customer"]["name"] != saved_name:
                save_customer_name(state["customer"]["name"])
                saved_name = state["customer"]["name"]
            
        except Exception as e:
            print(f"Error in step '{current_step}': {str(e)}")
            break
    
    print("\nWorkflow completed.")

if __name__ == "__main__":
    main() 