# Fixed implementation of workflowbond7.py with no recursion issues

from typing import TypedDict, Dict, Any, List, Annotated
from langgraph.graph import StateGraph, END
import os
from langsmith.run_helpers import traceable
import json
from datetime import datetime
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph import add_messages
import sys
from functools import lru_cache

# Safe environment variable handling
try:
    from langchain_openai import ChatOpenAI
    import openai
except ImportError:
    print("Warning: langchain_openai or openai not available")

# Enhanced State Definition for 007 Productivity Agent
class AgentState(TypedDict):
    user: dict  # Store user information (name, preferences)
    todos: list  # Store todo items
    messages: Annotated[List[BaseMessage], add_messages]  # For conversation tracking
    current_step: str  # For tracking workflow progress
    skills_used: list  # Track which skills were used in the session
    human_input_received: bool  # Flag to indicate if we've received human input

# Initialize Models with error handling
@lru_cache(maxsize=4)
def get_model():
    """Get a model for generating responses"""
    try:
        model = ChatOpenAI(temperature=0.7, model_name="gpt-4o")
        return model
    except Exception as e:
        print(f"Error initializing model: {str(e)}")
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
    if "human_input_received" not in state:
        state["human_input_received"] = False
        
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
        greeting = f"Hello {user_name}! I'm 007, your personal productivity agent. How can I help you today?"
    else:
        greeting = "Hello! I'm 007, your personal productivity agent. I don't think we've met before. What's your name?"
    
    # Add the greeting as a system message
    system_prompt = """You are 007, a personal productivity agent.
You help users manage their tasks, find information, and boost their productivity.
You initially have some limitations, but those will improve soon.
Your current skills:
1. Remember and manage to-do items
2. Call external services to shop for what the user wants and provide information"""
    
    # Add the messages
    messages = [
        SystemMessage(content=system_prompt),
        AIMessage(content=greeting)
    ]
    
    return {
        "messages": messages,
        "current_step": "human_step"  # Go to the human_step node to wait for input
    }

@traceable(project_name="007-productivity-agent")
def human_step(state: AgentState):
    """Wait for human input - this is an explicit step to prevent recursion"""
    
    # Check if we have a human message as the last message
    if state["messages"] and len(state["messages"]) > 0:
        last_message = state["messages"][-1]
        if isinstance(last_message, HumanMessage):
            # We have received human input, so process it
            return {
                "human_input_received": True,
                "current_step": "process_input"
            }
    
    # No human input received, so just stay in this state
    # This is a terminal state for the graph until external input is provided
    return {
        "current_step": END
    }

@traceable(project_name="007-productivity-agent")
def process_input(state: AgentState):
    """Process user input and determine next action"""
    # Reset the human_input_received flag
    state["human_input_received"] = False
    
    # Get the latest message from the user
    latest_message = state["messages"][-1]
    message_content = latest_message.content
    
    # If we're still in the introduction phase and don't know the user's name
    if state["user"].get("name") is None:
        # Extract name from message
        name = message_content.strip()
        if len(name) > 0:
            # Update user info
            return {
                "user": {"name": name},
                "messages": [AIMessage(content=f"Nice to meet you, {name}! How can I help you today?")],
                "current_step": "human_step"
            }
    
    # Determine intent based on keywords
    intent = "general_question"  # Default intent
    lower_content = message_content.lower()
    
    if "add" in lower_content and ("todo" in lower_content or "task" in lower_content):
        intent = "add_todo"
    elif "show" in lower_content and ("todo" in lower_content or "task" in lower_content):
        intent = "view_todos"
    elif "list" in lower_content and ("todo" in lower_content or "task" in lower_content):
        intent = "view_todos"
    elif any(word in lower_content for word in ["bye", "exit", "quit", "goodbye"]):
        intent = "end_conversation"
    
    # Add the intent to skills used
    skills_used = state["skills_used"] 
    if intent not in skills_used:
        skills_used.append(intent)
    
    # Route to appropriate action
    return {
        "skills_used": skills_used,
        "current_step": intent
    }

@traceable(project_name="007-productivity-agent")
def add_todo(state: AgentState):
    """Add a task to the todo list"""
    
    latest_message = state["messages"][-1].content
    
    # Extract task from the message - remove "add" and "todo" keywords
    task = latest_message
    lower_task = task.lower()
    
    # Simple task extraction
    if ":" in task:
        task = task.split(":", 1)[1].strip()
    elif "add" in lower_task and "task" in lower_task:
        task = task.lower().replace("add", "", 1)
        task = task.replace("task", "", 1)
        task = task.strip()
    elif "add" in lower_task and "todo" in lower_task:
        task = task.lower().replace("add", "", 1)
        task = task.replace("todo", "", 1)
        task = task.strip()
    
    # Add to todos
    todos = state["todos"]
    todos.append({"task": task, "created_at": datetime.now().isoformat()})
    
    return {
        "todos": todos,
        "messages": [AIMessage(content=f"I've added \"{task}\" to your todo list. Is there anything else you'd like me to do?")],
        "current_step": "human_step"
    }

@traceable(project_name="007-productivity-agent")
def view_todos(state: AgentState):
    """Show the todo list"""
    
    todos = state["todos"]
    
    if not todos:
        response = "You don't have any tasks in your todo list yet. Would you like to add one?"
    else:
        response = "Here's your current todo list:\n"
        for i, todo in enumerate(todos, 1):
            response += f"{i}. {todo['task']}\n"
        response += "\nIs there anything else you'd like me to do?"
    
    return {
        "messages": [AIMessage(content=response)],
        "current_step": "human_step"
    }

@traceable(project_name="007-productivity-agent")
def general_question(state: AgentState):
    """Handle general questions"""
    
    # Get the latest message
    latest_message = state["messages"][-1]
    
    # Use a simple rule-based response system
    content = latest_message.content.lower()
    
    # Default response
    response = "I'm here to help you stay productive. Would you like to add a task to your todo list or see your current tasks?"
    
    # Check for common phrases
    if "hello" in content or "hi" in content:
        response = "Hello there! How can I help you today with your productivity tasks?"
    elif "how are you" in content:
        response = "I'm functioning perfectly! Thank you for asking. How can I help you with your tasks today?"
    elif "help" in content:
        response = "I can help you manage your tasks and boost your productivity. Try asking me to add a task or show your to-do list!"
    elif "thank" in content:
        response = "You're welcome! Is there anything else I can help you with?"
    elif "langgraph" in content:
        response = "LangGraph is a powerful framework for building AI applications with structured workflows. It's what makes me work!"
    elif "langchain" in content:
        response = "LangChain is a framework for developing applications powered by language models. It's a key technology behind agents like me."
    elif "capability" in content or "do you do" in content or "can you" in content:
        response = "I can help you manage your tasks with my to-do list functionality. I can add tasks, show your current tasks, and chat with you about productivity topics."
    
    try:
        # Try to use the model if available
        model = get_model()
        if model:
            # Only use the last few messages to keep context small
            context = state["messages"][-5:]  # Last 5 messages max
            model_response = model.invoke(context)
            if model_response and model_response.content:
                response = model_response.content
    except Exception as e:
        print(f"Error using model: {str(e)}")
        # Continue with rule-based response
    
    return {
        "messages": [AIMessage(content=response)],
        "current_step": "human_step"
    }

@traceable(project_name="007-productivity-agent")
def end_conversation(state: AgentState):
    """End the conversation"""
    
    # Create a summary of what was accomplished
    tasks_added = len(state["todos"])
    skills_used = state["skills_used"]
    
    farewell = f"It was great helping you today! "
    if tasks_added > 0:
        farewell += f"I've added {tasks_added} tasks to your todo list. "
    farewell += "Feel free to come back anytime you need assistance with your productivity."
    
    return {
        "messages": [AIMessage(content=farewell)],
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
    workflow.add_node("human_step", human_step)  # This is a special node that waits for human input
    workflow.add_node("process_input", process_input)
    workflow.add_node("add_todo", add_todo)
    workflow.add_node("view_todos", view_todos)
    workflow.add_node("general_question", general_question)
    workflow.add_node("end_conversation", end_conversation)
    
    # Define edges
    workflow.add_edge("validate_input", "initialize_agent")
    workflow.add_edge("initialize_agent", "generate_greeting")
    workflow.add_edge("generate_greeting", "human_step")
    
    # From human_step, conditionally go to process_input if human input is received
    workflow.add_conditional_edges(
        "human_step",
        lambda state: state["current_step"],
        {
            "process_input": "process_input",
            END: END  # End the current execution if no human input
        }
    )
    
    # From process_input, go to specific handlers
    workflow.add_conditional_edges(
        "process_input",
        lambda state: state["current_step"],
        {
            "add_todo": "add_todo",
            "view_todos": "view_todos", 
            "general_question": "general_question",
            "end_conversation": "end_conversation",
            "human_step": "human_step"
        }
    )
    
    # All handlers go back to human_step
    workflow.add_edge("add_todo", "human_step")
    workflow.add_edge("view_todos", "human_step")
    workflow.add_edge("general_question", "human_step")
    
    # Set entry point
    workflow.set_entry_point("validate_input")
    
    return workflow

# Create the compiled application
app = create_agent_graph().compile()

# Main function for local testing
def main():
    """Run the agent workflow for local testing"""
    
    workflow = create_agent_graph().compile()
    
    # Initial empty state
    state = {
        "messages": [],
        "user": {"name": None},
        "todos": [],
        "skills_used": [],
        "human_input_received": False,
        "current_step": "validate_input"
    }
    
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
            # If the workflow ended, break out
            if result["current_step"] == END:
                break
                
            # Get user input
            user_input = input("\nYou: ")
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\nExiting conversation. Goodbye!")
                break
            
            # Add user message to state
            result_copy = result.copy()
            result_copy["messages"].append(HumanMessage(content=user_input))
            result_copy["human_input_received"] = True
            
            # Invoke workflow
            try:
                result = workflow.invoke(result_copy)
                
                # Print agent's response
                for message in result["messages"]:
                    if isinstance(message, AIMessage) and message not in result_copy["messages"]:
                        print(f"Agent: {message.content}")
                
                # Check if workflow ended
                if result["current_step"] == END:
                    break
            except Exception as e:
                print(f"\nError processing your request: {str(e)}")
                print("Let's try again.")
                
                # Continue the conversation
                result = result_copy
    except Exception as e:
        print(f"\n❌ Error running agent: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()