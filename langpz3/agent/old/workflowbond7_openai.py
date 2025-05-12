# Fixed implementation of workflowbond7.py with OpenAI integration and no recursion issues

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


class MockLanguageModel:
    """A mock model that logs calls and returns predefined responses"""
    
    def __init__(self, name):
        self.name = name
        self.call_count = 0
        # Predefined responses for different contexts
        self.responses = {
            "greeting": "Hello! I'm 007, your personal productivity agent. I don't think we've met before. What's your name?",
            "task_added": "I've added that task to your list. Is there anything else you'd like me to help you with?",
            "name_intro": "Nice to meet you! How can I help you today? I can help with tasks, finding information, and more.",
            "fallback": "I understand. How can I assist you further?"
        }
    
    def __call__(self, messages, *args, **kwargs):
        """Make the object callable like a real LLM"""
        self.call_count += 1
        print(f"🔍 MOCK MODEL ({self.name}) CALLED (call #{self.call_count})")
        print(f"📥 Input messages: {len(messages)} message(s)")
        
        # Get the last message to help with context detection
        last_msg = None
        if messages and len(messages) > 0:
            last_msg = messages[-1]
            last_content = getattr(last_msg, 'content', str(last_msg))
            print(f"📄 Last message content (sample): {last_content[:100]}...")
        
        # Determine which response to use based on message content
        response_key = "fallback"
        
        # If system prompt mentions name introduction
        system_content = ""
        for msg in messages:
            if getattr(msg, 'type', '') == 'system':
                system_content = getattr(msg, 'content', '')
                break
                
        if "just learned their name" in system_content or "what's your name" in system_content:
            response_key = "name_intro"
        elif last_msg and "task" in getattr(last_msg, 'content', '').lower():
            response_key = "task_added"
        elif any("name" in str(m).lower() for m in messages):
            response_key = "greeting"
        
        response_text = self.responses[response_key]
        print(f"📤 Responding with: {response_key} -> {response_text[:50]}...")
        
        # Create a response object similar to what the real model would return
        return AIMessage(content=response_text)
    
    def bind(self, system_message=None):
        """Support the bind method that real models have"""
        print(f"🔄 Mock model bind called with system message: {system_message[:50] if system_message else 'None'}")
        return self

@traceable(project_name="007-productivity-agent")
def process_input(state: AgentState):
    """Process user input and generate a response using the language model"""
    print("🏁 Entering process_input function")
    
    # Get current messages
    messages = state.get("messages", [])
    print(f"📊 Current message count: {len(messages)}")
    
    # Find the last human message
    last_human_message = None
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            last_human_message = message
            break
    
    if not last_human_message:
        print("⚠️ No human message found in state")
        return state
    
    print(f"👤 Last human message: {last_human_message.content[:100]}...")
    
    # Check if this is a name introduction
    is_name_introduction = False
    if len(messages) >= 2:
        # The previous ai message was asking for name, and this is the first human response
        prev_ai_message = None
        for msg in reversed(messages[:-1]):  # All but the last message (which is the human's)
            if isinstance(msg, AIMessage):
                prev_ai_message = msg
                break
        
        if prev_ai_message and "what's your name" in prev_ai_message.content.lower():
            is_name_introduction = True
            print("🔍 Detected name introduction context")
    
    # Process name introduction if detected
    if is_name_introduction:
        # Extract name
        name_parts = last_human_message.content.split("my name is ")
        if len(name_parts) > 1:
            name = name_parts[1].strip()
        else:
            name = last_human_message.content.strip()
        
        # Update user name in state
        state["user"]["name"] = name
        print(f"📊 Updated user name to: {name}")
        
        # Determine if we're in mocked mode
        is_mocked = os.environ.get("MOCK_MODE", "False").lower() == "true"
        print(f"⚙️ process_input: Mocked mode = {is_mocked}")
        
        if is_mocked:
            # Use predefined response in mocked mode
            response_content = f"Nice to meet you, {name}! How can I help you today? I can help you manage tasks, find information, or assist with your productivity needs."
            print(f"🔄 Using pre-defined response in mocked mode: {response_content[:50]}...")
            response = AIMessage(content=response_content)
        else:
            # Prepare system prompt for model
            system_prompt = f"""You are 007, a personal productivity agent.
You help users manage their tasks, find information, and boost their productivity.
The user's name is {name}. You've just learned their name, so respond warmly and introduce your capabilities.
Keep your response concise and friendly."""
            
            # Get model
            try:
                print("🚀 Calling OpenAI model to generate response")
                model = _get_model("openai", system_prompt, mocked=is_mocked)
                
                import time
                start_time = time.time()
                response = model(messages)
                end_time = time.time()
                
                print(f"✅ Response generated in {end_time - start_time:.2f}s")
                print(f"💬 Response content: {response.content[:100]}...")
            except Exception as e:
                print(f"❌ Error calling model: {str(e)}")
                response = AIMessage(content=f"Nice to meet you, {name}! How can I help you today?")
    else:
        # This is a regular message, not a name introduction
        # Determine if we're in mocked mode
        is_mocked = os.environ.get("MOCK_MODE", "False").lower() == "true"
        print(f"⚙️ process_input: Mocked mode = {is_mocked}")
        
        if is_mocked:
            # Simplified logic for mocked responses
            if "task" in last_human_message.content.lower() or "todo" in last_human_message.content.lower():
                response_content = "I've noted that task. Would you like me to add anything else to your list?"
            elif "help" in last_human_message.content.lower() or "what can you do" in last_human_message.content.lower():
                response_content = "I can help you manage tasks, find information, and boost your productivity. What would you like assistance with today?"
            else:
                response_content = "I understand. Is there anything specific you'd like help with today?"
            
            print(f"🔄 Using pre-defined response in mocked mode: {response_content[:50]}...")
            response = AIMessage(content=response_content)
        else:
            # Get user name if available
            user_name = state["user"].get("name", "")
            
            # Prepare system prompt for model
            system_prompt = f"""You are 007, a personal productivity agent.
You help users manage their tasks, find information, and boost their productivity.
You have a friendly, helpful tone.
The user's name is {user_name if user_name else 'unknown'}.
Keep your responses concise and focused."""
            
            # Get model
            try:
                print("🚀 Calling OpenAI model to generate response")
                model = _get_model("openai", system_prompt, mocked=is_mocked)
                
                import time
                start_time = time.time()
                response = model(messages)
                end_time = time.time()
                
                print(f"✅ Response generated in {end_time - start_time:.2f}s")
                print(f"💬 Response content: {response.content[:100]}...")
            except Exception as e:
                print(f"❌ Error calling model: {str(e)}")
                response = AIMessage(content="I understand. Is there anything specific you'd like help with today?")
    
    # Add the response to messages
    messages.append(response)
    
    # Skills tracking - simple version
    skills_used = state.get("skills_used", [])
    if "task" in last_human_message.content.lower() or "todo" in last_human_message.content.lower():
        if "task_management" not in skills_used:
            skills_used.append("task_management")
    
    # Update the state with new messages and other changes
    return {
        **state,
        "messages": messages,
        "skills_used": skills_used,
        "current_step": "process_input"  # Loop back to handle next input
    }

# Initialize Models with error handling
@lru_cache(maxsize=4)
def _get_model(model_name: str, system_prompt: str = None, mocked: bool = False):
    """Get a language model, with improved logging for mocked vs real mode"""
    print(f"📝 _get_model called with: model_name={model_name}, mocked={mocked}")
    
    try:
        if mocked:
            print("🔄 Using MOCKED model implementation")
            # Return a callable mock that logs what it receives
            return MockLanguageModel(model_name)
        
        if model_name == "openai":
            print("🔌 Initializing REAL OpenAI model (gpt-4o)")
            model = ChatOpenAI(temperature=0, model_name="gpt-4o")
        else:
            raise ValueError(f"Unsupported model type: {model_name}")
        
        if system_prompt:
            print(f"🧠 Binding system prompt: {system_prompt[:50]}...")
            model = model.bind(system_message=system_prompt)
        
        return model
    except Exception as e:
        print(f"❌ Error initializing model: {str(e)}")
        # Return a mock model if initialization fails
        print("⚠️ Returning MockLanguageModel as fallback")
        return MockLanguageModel(f"error-fallback-{model_name}")

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
    """Generate the initial greeting for the user with enhanced logging"""
    print("🏁 Entering generate_greeting function")
    
    # Check if we know the user's name
    user_name = state["user"].get("name")
    print(f"📊 User name from state: {user_name}")
    
    # Determine if we're in mocked mode
    is_mocked = os.environ.get("MOCK_MODE", "False").lower() == "true"
    print(f"⚙️ generate_greeting: Mocked mode = {is_mocked}")
    
    # Construct the system prompt
    system_prompt = """You are 007, a personal productivity agent.
You help users manage their tasks, find information, and boost their productivity.
You initially have some limitations, but those will improve soon.
Your current skills:
1. Remember and manage to-do items
2. Call external services to shop for what the user wants and provide information"""
    
    # Determine greeting message - either via model in live mode or directly in mocked mode
    if is_mocked:
        print("🔄 Using pre-defined greeting in mocked mode")
        if user_name:
            greeting = f"Hello {user_name}! I'm 007, your personal productivity agent. How can I help you today?"
        else:
            greeting = "Hello! I'm 007, your personal productivity agent. I don't think we've met before. What's your name?"
    else:
        # In live mode, we'd normally let the model generate this, but for simplicity:
        print("🔌 Would normally call OpenAI model here in live mode")
        if user_name:
            greeting = f"Hello {user_name}! I'm 007, your personal productivity agent. How can I help you today?"
        else:
            greeting = "Hello! I'm 007, your personal productivity agent. I don't think we've met before. What's your name?"
    
    print(f"💬 Greeting message: {greeting}")
    
    # Add the messages
    messages = [
        SystemMessage(content=system_prompt),
        AIMessage(content=greeting)
    ]
    
    print(f"✅ generate_greeting complete, returning {len(messages)} messages")
    return {
        "messages": messages,
        "current_step": "process_input"
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
    """Handle general questions using OpenAI"""
    
    try:
        # Try to use the model
        model = get_model()
        if model:
            # Only use the last few messages to keep context small
            context = state["messages"][-5:]  # Last 5 messages max
            model_response = model.invoke(context)
            if model_response and model_response.content:
                return {
                    "messages": [AIMessage(content=model_response.content)],
                    "current_step": "human_step"
                }
    except Exception as e:
        print(f"Error using model for general question: {str(e)}")
        # Fall through to rule-based response
    
    # Fallback to rule-based responses
    latest_message = state["messages"][-1]
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