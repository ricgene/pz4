import pytest
from unittest.mock import MagicMock, patch, ANY
from workflow050825 import (
    WorkflowState,
    validate_input,
    initialize_workflow,
    process_name,
    analyze_sentiment,
    human_step,
    create_workflow,
    save_customer_name,
    load_customer_name
)
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import END

@pytest.fixture
def empty_state():
    """Create an empty state for testing"""
    return {
        "customer": {"name": None},
        "task": {"description": None, "status": "new"},
        "vendor": {"name": "Dave's Plumbing", "email": "dave@plumbing.com"},
        "messages": [],
        "sentiment": "neutral",
        "sentiment_attempts": 0,
        "step_counts": {},
        "human_input_received": False,
        "skills_used": [],
        "processed_inputs": []
    }

@pytest.fixture
def workflow():
    """Create a workflow instance for testing"""
    return create_workflow()

def test_validate_input_initializes_state(empty_state):
    """Test that validate_input properly initializes all required fields"""
    result = validate_input(empty_state)
    
    # Check that all required fields are present
    assert "customer" in result
    assert "task" in result
    assert "vendor" in result
    assert "messages" in result
    assert "sentiment" in result
    assert "sentiment_attempts" in result
    assert "step_counts" in result
    assert "human_input_received" in result
    assert "skills_used" in result
    assert "processed_inputs" in result
    
    # Check default values
    assert result["sentiment"] == "neutral"
    assert result["sentiment_attempts"] == 0
    assert result["human_input_received"] is False
    assert isinstance(result["skills_used"], list)
    assert isinstance(result["processed_inputs"], list)
    assert isinstance(result["step_counts"], dict)

def test_initialize_workflow_without_name(empty_state):
    """Test workflow initialization when no name is present"""
    result = initialize_workflow(empty_state)
    
    assert "messages" in result
    assert len(result["messages"]) == 2
    assert isinstance(result["messages"][0], SystemMessage)
    assert isinstance(result["messages"][1], AIMessage)
    assert "What's your name?" in result["messages"][1].content
    assert result["current_step"] == "process_name"
    assert "initialize" in empty_state["skills_used"]

def test_initialize_workflow_with_name(empty_state):
    """Test workflow initialization when name is present"""
    empty_state["customer"]["name"] = "John"
    result = initialize_workflow(empty_state)
    
    assert "messages" in result
    assert len(result["messages"]) == 2
    assert "John" in result["messages"][1].content
    assert "meet with Dave's Plumbing" in result["messages"][1].content
    assert result["current_step"] == "check_contractor_meeting"

def test_process_name_with_empty_input(empty_state):
    """Test name processing with empty input"""
    empty_state["messages"].append(HumanMessage(content=""))
    result = process_name(empty_state)
    
    assert result["current_step"] == "human_step"
    assert len(empty_state["messages"]) == 2  # Updated to expect error message
    assert "didn't catch your name" in empty_state["messages"][1].content
    assert "process_name" in empty_state["skills_used"]

def test_process_name_with_valid_input(empty_state):
    """Test name processing with valid input"""
    empty_state["messages"].append(HumanMessage(content="John Smith"))
    result = process_name(empty_state)
    
    assert result["current_step"] == "analyze_sentiment"
    assert empty_state["customer"]["name"] == "John Smith"
    assert len(empty_state["messages"]) == 2
    assert "Thanks John Smith" in empty_state["messages"][1].content

def test_analyze_sentiment_positive(empty_state):
    """Test sentiment analysis with positive response"""
    empty_state["messages"].append(HumanMessage(content="Yes, I'd like to schedule it"))
    result = analyze_sentiment(empty_state)
    
    assert result["current_step"] == "confirm_end"
    assert empty_state["sentiment"] == "positive"
    assert "analyze_sentiment" in empty_state["skills_used"]

def test_analyze_sentiment_negative(empty_state):
    """Test sentiment analysis with negative response"""
    empty_state["messages"].append(HumanMessage(content="No, I need to reschedule"))
    result = analyze_sentiment(empty_state)
    
    assert result["current_step"] == "reschedule"
    assert empty_state["sentiment"] == "negative"

def test_analyze_sentiment_unclear(empty_state):
    """Test sentiment analysis with unclear response"""
    empty_state["messages"].append(HumanMessage(content="Maybe later"))
    result = analyze_sentiment(empty_state)
    
    assert result["current_step"] == "human_step"
    assert empty_state["sentiment"] == "unclear"
    assert "not sure" in empty_state["messages"][-1].content

def test_human_step_with_duplicate_input(empty_state):
    """Test human step handling duplicate input"""
    empty_state["processed_inputs"].append("Hello")
    empty_state["messages"].append(HumanMessage(content="Hello"))
    result = human_step(empty_state)
    
    assert result["current_step"] == "human_step"
    assert "already processed" in empty_state["messages"][-1].content

def test_human_step_with_end_command(empty_state):
    """Test human step handling end command"""
    empty_state["messages"].append(HumanMessage(content="end"))
    result = human_step(empty_state)
    
    assert result["current_step"] == END
    assert "Thank you" in empty_state["messages"][-1].content

def test_human_step_with_question(empty_state):
    """Test human step handling question"""
    empty_state["messages"].append(HumanMessage(content="What time is the installation?"))
    result = human_step(empty_state)
    
    assert result["current_step"] == "process_additional"

def test_create_workflow_structure():
    """Test workflow graph structure"""
    workflow = create_workflow()
    
    # Verify nodes exist
    assert "validate" in workflow.nodes
    assert "initialize" in workflow.nodes
    assert "process_name" in workflow.nodes
    assert "analyze_sentiment" in workflow.nodes
    assert "human_step" in workflow.nodes
    
    # Verify edges by checking the graph structure
    # Since we're working with a compiled graph, we'll verify the key transitions
    graph = workflow.get_graph()
    
    # Helper function to check if an edge exists
    def has_edge(source: str, target: str) -> bool:
        return any(
            e.source == source and e.target == target
            for e in graph.edges
        )
    
    # Verify key edges exist
    assert has_edge("validate", "initialize"), "Missing edge: validate -> initialize"
    assert has_edge("process_name", "human_step"), "Missing edge: process_name -> human_step"
    assert has_edge("analyze_sentiment", "human_step"), "Missing edge: analyze_sentiment -> human_step"

def test_save_and_load_customer_name(tmp_path):
    """Test customer name persistence"""
    test_name = "John Smith"
    test_file = tmp_path / "test_customer.json"
    
    # Test saving
    save_customer_name(test_name, str(test_file))
    assert test_file.exists()
    
    # Test loading
    loaded_name = load_customer_name(str(test_file))
    assert loaded_name == test_name

def test_recursion_protection(empty_state):
    """Test recursion protection in workflow steps"""
    # Test process_name recursion
    empty_state["step_counts"]["process_name"] = 6
    result = process_name(empty_state)
    assert result["current_step"] == END
    assert "trouble understanding" in empty_state["messages"][-1].content
    
    # Test analyze_sentiment recursion
    empty_state["step_counts"]["analyze_sentiment"] = 6
    result = analyze_sentiment(empty_state)
    assert result["current_step"] == END
    assert "trouble understanding" in empty_state["messages"][-1].content
    
    # Test human_step recursion
    empty_state["step_counts"]["human_step"] = 6
    result = human_step(empty_state)
    assert result["current_step"] == END
    assert "trouble understanding" in empty_state["messages"][-1].content

def test_workflow_integration(workflow, empty_state):
    """Test complete workflow integration"""
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    
    # Start with validation and initialization
    state = empty_state.copy()
    state = workflow.invoke(state)
    
    # Verify initialization
    assert len(state["messages"]) > 0
    assert isinstance(state["messages"][0], SystemMessage)
    assert state["current_step"] == "process_name"
    
    # Process name
    state = workflow.invoke({
        **state,
        "messages": state["messages"] + [HumanMessage(content="John Smith")]
    })
    assert state["customer"]["name"] == "John Smith"
    assert state["current_step"] == "analyze_sentiment"
    
    # Respond positively to scheduling
    state = workflow.invoke({
        **state,
        "messages": state["messages"] + [HumanMessage(content="Yes, I'd like to schedule it")]
    })
    assert state["sentiment"] == "positive"
    assert state["current_step"] == "human_step"
    
    # End conversation
    state = workflow.invoke({
        **state,
        "messages": state["messages"] + [HumanMessage(content="end")]
    })
    assert state["current_step"] == END 