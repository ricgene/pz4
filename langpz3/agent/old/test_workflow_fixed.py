#!/usr/bin/env python
"""
Test suite for workflow_fixed.py
Tests the contractor workflow implementation including state management, sentiment analysis,
and conversation flow.
"""

import os
import json
import pytest
from typing import Dict, Any
from unittest.mock import patch, MagicMock, ANY
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import END
from workflow_fixed import (
    WorkflowState,
    validate_input,
    initialize_workflow,
    process_name,
    process_schedule,
    analyze_sentiment,
    confirm_end,
    process_additional,
    create_workflow
)

# Test data
TEST_CUSTOMER = {
    "name": "John Smith",
    "email": "john.smith@example.com",
    "phoneNumber": "555-123-4567",
    "zipCode": "94105"
}

TEST_TASK = {
    "description": "Kitchen faucet installation",
    "category": "Plumbing"
}

TEST_VENDOR = {
    "name": "Dave's Plumbing",
    "email": "dave@plumbing.com",
    "phoneNumber": "555-987-6543"
}

def create_test_state(customer: Dict = None, task: Dict = None, vendor: Dict = None) -> WorkflowState:
    """Create a test state with optional overrides"""
    return {
        "customer": customer or TEST_CUSTOMER,
        "task": task or TEST_TASK,
        "vendor": vendor or TEST_VENDOR,
        "messages": [],
        "current_step": "validate",
        "sentiment": "neutral",
        "sentiment_attempts": 0
    }

def test_validate_input():
    """Test input validation"""
    # Test with complete data
    state = create_test_state()
    result = validate_input(state)
    assert "current_step" in result
    assert result["current_step"] == "validate"
    assert "customer" in result
    assert "task" in result
    assert "vendor" in result

    # Test with missing data
    empty_state = {}
    result = validate_input(empty_state)
    assert "customer" in result
    assert "task" in result
    assert "vendor" in result
    assert result["vendor"]["name"] == "Dave's Plumbing"

def test_initialize_workflow():
    """Test workflow initialization"""
    # Test with existing customer name
    state = create_test_state()
    result = initialize_workflow(state)
    assert "messages" in result
    assert len(result["messages"]) == 2
    assert isinstance(result["messages"][0], SystemMessage)
    assert isinstance(result["messages"][1], AIMessage)
    assert "current_step" in result

    # Test without customer name
    state = create_test_state(customer={"name": None})
    result = initialize_workflow(state)
    assert "messages" in result
    assert len(result["messages"]) == 2
    assert "current_step" in result
    assert result["current_step"] == "process_name"

def test_process_name():
    """Test name processing"""
    # Test with valid name
    state = create_test_state()
    state["messages"] = [HumanMessage(content="John Smith")]
    result = process_name(state)
    assert "customer" in result
    assert result["customer"]["name"] == "John Smith"
    assert "messages" in result
    assert len(result["messages"]) > 1
    assert "current_step" in result

    # Test with no messages
    state = create_test_state()
    result = process_name(state)
    assert result["current_step"] == "initialize"

def test_analyze_sentiment():
    """Test sentiment analysis"""
    # Test positive sentiment
    state = create_test_state()
    state["messages"] = [HumanMessage(content="Yes, I'd love to schedule it for tomorrow!")]
    result = analyze_sentiment(state)
    assert "sentiment" in result
    assert "current_step" in result

    # Test negative sentiment
    state = create_test_state()
    state["messages"] = [HumanMessage(content="No, I can't do tomorrow")]
    result = analyze_sentiment(state)
    assert "sentiment" in result
    assert "current_step" in result

    # Test unclear sentiment
    state = create_test_state()
    state["messages"] = [HumanMessage(content="Maybe")]
    result = analyze_sentiment(state)
    assert "sentiment" in result
    assert "current_step" in result

def test_confirm_end():
    """Test end confirmation"""
    # Test with yes
    state = create_test_state()
    state["messages"] = [HumanMessage(content="Yes, I have one more question")]
    result = confirm_end(state)
    assert "current_step" in result
    assert result["current_step"] == "process_additional"

    # Test with no
    state = create_test_state()
    state["messages"] = [HumanMessage(content="No, that's all")]
    result = confirm_end(state)
    assert "current_step" in result
    assert result["current_step"] == "__end__"

def test_process_additional():
    """Test processing additional requests"""
    state = create_test_state()
    state["messages"] = [HumanMessage(content="Can you make sure they bring extra parts?")]
    result = process_additional(state)
    assert "current_step" in result
    assert result["current_step"] == "confirm_end"

@patch('workflow_fixed.StateGraph')
def test_create_workflow(mock_state_graph):
    """Test workflow creation with mocked StateGraph"""
    # Create mock instance
    mock_graph_instance = MagicMock()
    mock_state_graph.return_value = mock_graph_instance
    
    # Create the workflow
    workflow = create_workflow()
    
    # Verify StateGraph was instantiated with WorkflowState
    mock_state_graph.assert_called_once_with(WorkflowState)
    
    # Verify all nodes were added
    expected_nodes = [
        "validate",
        "initialize",
        "process_name",
        "process_schedule",
        "confirm_end",
        "process_additional",
        "analyze_sentiment",
        "reschedule",
        "process_notes",
        "human_step",
        "check_contractor_meeting"
    ]
    
    for node in expected_nodes:
        mock_graph_instance.add_node.assert_any_call(node, ANY)
    
    # Verify entry point was set
    mock_graph_instance.set_entry_point.assert_called_once_with("validate")
    
    # Verify edges were added
    expected_edges = [
        ("validate", "initialize"),
        ("initialize", "human_step"),
        ("human_step", "process_name"),
        ("human_step", "check_contractor_meeting"),
        ("process_name", "process_schedule"),
        ("process_schedule", "confirm_end"),
        ("confirm_end", "process_additional"),
        ("process_additional", "confirm_end"),
        ("process_schedule", "analyze_sentiment"),
        ("analyze_sentiment", "reschedule"),
        ("analyze_sentiment", END),
        ("human_step", "reschedule"),
        ("reschedule", END),
        ("process_notes", "end"),
        ("end", END),
        ("check_contractor_meeting", "confirm_end")
    ]
    
    for from_node, to_node in expected_edges:
        mock_graph_instance.add_edge.assert_any_call(from_node, to_node)
    
    # Verify workflow was compiled
    mock_graph_instance.compile.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__]) 