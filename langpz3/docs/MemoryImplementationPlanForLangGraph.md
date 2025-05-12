# Memory Implementation Plan for LangGraph Agent

This document outlines the approach for adding memory capabilities to our existing LangGraph agent code.

## 1. Enhance the AgentState TypedDict

Our current `AgentState` already includes a `messages` field that stores conversation history. We'll enhance this to include more structured memory:

```python
class AgentState(TypedDict):
    user: dict                  # Store user information (name, preferences)
    todos: list                 # Store todo items
    messages: Annotated[List[BaseMessage], add_messages]  # Basic conversation history
    conversation_summary: str   # Summary of conversation history
    entity_memory: dict         # Store remembered entities and attributes
    current_step: str           # For tracking workflow progress
    skills_used: list           # Track which skills were used in the session
```

## 2. Add Memory Initialization

Create a new node function to initialize the memory structures:

```python
@traceable(project_name="007-productivity-agent")
def initialize_memory(state: AgentState):
    """Initialize memory components in the agent state"""
    
    state = state.copy()  # Create a copy to avoid mutation
    
    # Initialize entity memory if not present
    if "entity_memory" not in state:
        state["entity_memory"] = {}
        
    # Initialize conversation summary if not present
    if "conversation_summary" not in state:
        state["conversation_summary"] = ""
    
    return state
```

## 3. Add Memory Update Functions

Create functions to update different parts of memory:

```python
@traceable(project_name="007-productivity-agent")
def update_entity_memory(state: AgentState, entity_name: str, attributes: dict):
    """Update entity memory with information about an entity"""
    
    state = state.copy()
    entity_memory = state.get("entity_memory", {})
    
    # Get or create entity
    entity = entity_memory.get(entity_name, {})
    
    # Update with new attributes
    entity.update(attributes)
    
    # Store back in memory
    entity_memory[entity_name] = entity
    state["entity_memory"] = entity_memory
    
    return state

@traceable(project_name="007-productivity-agent")
def summarize_conversation(state: AgentState):
    """Create or update a summary of the conversation history"""
    
    # Only summarize if we have enough messages
    if not state.get("messages") or len(state["messages"]) < 5:
        return state
    
    model = _get_model("openai")
    if not model:
        return state
        
    messages = [
        SystemMessage(content="Summarize this conversation between a user and a productivity agent. Focus on key information and decisions."),
        HumanMessage(content=str([m.content for m in state["messages"]]))
    ]
    
    try:
        response = model.invoke(messages)
        state["conversation_summary"] = response.content
    except Exception as e:
        print(f"Error summarizing conversation: {str(e)}")
        
    return state
```

## 4. Modify Existing Process Input Node

Update the existing `process_input` function to use memory context:

```python
@traceable(project_name="007-productivity-agent")
def process_input(state: AgentState):
    """Process user input with memory context"""
    
    # Get latest message and user name as before
    latest_message = state["messages"][-1] if state["messages"] else None
    user_name = state["user"].get("name", "")
    
    # Include memory context in the system prompt
    entity_memory_text = ""
    if state.get("entity_memory"):
        entity_memory_text = "Known information:\n"
        for entity, attributes in state["entity_memory"].items():
            entity_memory_text += f"- {entity}: {attributes}\n"
    
    conversation_summary = ""
    if state.get("conversation_summary"):
        conversation_summary = f"Conversation summary: {state['conversation_summary']}\n"
    
    # Create an enhanced system prompt with memory
    system_prompt = f"""You are 007, a personal productivity agent.
You help users manage their tasks, find information, and boost your productivity.
The user's name is {user_name if user_name else 'unknown'}.
{conversation_summary}
{entity_memory_text}
"""
    
    # Rest of your existing process_input function logic...
```

## 5. Update the Workflow Graph

Modify your `create_agent_graph` function to include the new memory nodes:

```python
def create_agent_graph():
    """Create the workflow graph with memory capabilities"""
    # Create a new graph
    workflow = StateGraph(AgentState)
    
    # Add existing nodes
    workflow.add_node("validate_input", validate_input)
    workflow.add_node("initialize_agent", initialize_agent)
    
    # Add new memory nodes
    workflow.add_node("initialize_memory", initialize_memory)
    workflow.add_node("summarize_conversation", summarize_conversation)
    
    # Add your other existing nodes
    workflow.add_node("generate_greeting", generate_greeting)
    workflow.add_node("process_input", process_input)
    # ... other nodes ...
    
    # Define edges - insert memory initialization
    workflow.add_edge("validate_input", "initialize_agent")
    workflow.add_edge("initialize_agent", "initialize_memory")  # Insert memory init
    workflow.add_edge("initialize_memory", "generate_greeting")  # Continue flow
    
    # Add edge to summarize after several messages
    workflow.add_conditional_edges(
        "process_input",
        lambda state: "summarize" if len(state.get("messages", [])) % 5 == 0 else state["current_step"],
        {
            "summarize": "summarize_conversation",
            "add_todo": "add_todo",
            "view_todos": "view_todos", 
            "general_question": "general_question",
            "end_conversation": "end_conversation"
        }
    )
    
    # Connect the summarize node back to the flow
    workflow.add_conditional_edges(
        "summarize_conversation",
        lambda state: state["current_step"],
        {
            "add_todo": "add_todo",
            "view_todos": "view_todos", 
            "general_question": "general_question",
            "end_conversation": "end_conversation"
        }
    )
    
    # ... rest of your graph definition ...
```

## 6. Entity Memory Update Integration

Add logic to update entity memory when new information is learned:

```python
@traceable(project_name="007-productivity-agent")
def extract_and_store_entities(state: AgentState):
    """Extract entities from conversation and store in memory"""
    
    if not state.get("messages") or len(state["messages"]) == 0:
        return state
    
    # Get the last few messages for context
    recent_messages = state["messages"][-3:]
    
    # Use your model to extract entities
    model = _get_model("openai")
    if not model:
        return state
    
    extract_prompt = """Extract key entities and their attributes from this conversation.
Format as JSON: { "entities": [{"name": "entity_name", "attributes": {"key": "value"}}] }
Only include entities with high confidence."""
    
    try:
        messages = [
            SystemMessage(content=extract_prompt),
            HumanMessage(content=str([m.content for m in recent_messages]))
        ]
        
        response = model.invoke(messages)
        
        # Try to parse the response as JSON
        import json
        try:
            entity_data = json.loads(response.content)
            for entity in entity_data.get("entities", []):
                name = entity.get("name")
                attributes = entity.get("attributes", {})
                if name:
                    # Update the entity memory
                    state = update_entity_memory(state, name, attributes)
        except json.JSONDecodeError:
            print("Could not parse entity extraction response as JSON")
    except Exception as e:
        print(f"Error extracting entities: {str(e)}")
    
    return state
```

Then integrate this into your workflow:

```python
workflow.add_edge("process_input", "extract_and_store_entities")
workflow.add_conditional_edges(
    "extract_and_store_entities",
    lambda state: state["current_step"],
    {
        "add_todo": "add_todo",
        "view_todos": "view_todos", 
        "general_question": "general_question",
        "end_conversation": "end_conversation"
    }
)
```

## 7. Optional: Long-term Storage Integration

If you want to add GCP storage integration for long-term memory:

```python
@traceable(project_name="007-productivity-agent")
def backup_memory_to_gcp(state: AgentState):
    """Backup important memory to GCP for long-term storage"""
    
    # Only run this occasionally to avoid excessive API calls
    # For example, at the end of conversations or every 10 messages
    if not state.get("current_step") == "end_conversation":
        return state
    
    try:
        # Here you would implement the GCP storage logic
        # This is placeholder code - you'd need to implement the actual storage
        print("Would back up memory to GCP here")
        
        # Mark the time of backup
        state["last_memory_backup"] = datetime.now().isoformat()
    except Exception as e:
        print(f"Error backing up memory: {str(e)}")
    
    return state
```

And add it to your workflow before ending the conversation:

```python
workflow.add_edge("end_conversation", "backup_memory_to_gcp")
workflow.add_edge("backup_memory_to_gcp", END)
```

With this plan, you now have a blueprint for adding memory capabilities to your agent in Cursor. You can adapt and implement these components as needed for your specific requirements.
