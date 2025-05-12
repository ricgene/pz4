#!/usr/bin/env python
"""
Integration tests for workflow_fixed.py
Tests the complete workflow with real interactions and state transitions.
"""

import os
import pytest
from typing import Dict, Any
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from workflow_fixed import (
    WorkflowState,
    create_workflow,
    get_llm
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
    "category": "Plumbing",
    "schedule": None
}

TEST_VENDOR = {
    "name": "Dave's Plumbing",
    "email": "dave@plumbing.com",
    "phoneNumber": "555-987-6543"
}

def create_test_state() -> WorkflowState:
    """Create a test state with default values"""
    return {
        "customer": {"name": None},
        "task": {"description": "Kitchen faucet installation"},
        "vendor": {"name": "Dave's Plumbing", "email": "dave@plumbing.com"},
        "messages": [],
        "sentiment": "neutral",
        "sentiment_attempts": 0,
        "step_counts": {
            "process_name": 0,
            "analyze_sentiment": 0,
            "confirm_end": 0,
            "process_additional": 0,
            "reschedule": 0
        },
        "human_input_received": False,
        "current_step": "validate"
    }

@pytest.fixture
def mock_input(monkeypatch):
    """Mock the input function for testing"""
    mock = MagicMock()
    monkeypatch.setattr("builtins.input", mock)
    return mock

@pytest.fixture
def workflow():
    """Create a workflow instance for testing"""
    return create_workflow()

def test_complete_happy_path(workflow, mock_input):
    """Test complete workflow with positive responses"""
    # Setup mock inputs for the conversation
    mock_input.side_effect = [
        "Alice Smith",  # Name
        "Yes",  # Schedule confirmation
        "",  # End conversation
    ]
    
    # Initial state
    state = create_test_state()
    
    # Run the workflow
    next_state = workflow.invoke(state)
    
    # Verify the workflow completed successfully
    assert next_state["current_step"] == END
    assert next_state["customer"]["name"] == "Alice Smith"
    assert any("Thank you" in msg.content for msg in next_state["messages"] if isinstance(msg, AIMessage))

def test_reschedule_flow(workflow, mock_input):
    """Test workflow with rescheduling"""
    # Setup mock inputs for the conversation
    mock_input.side_effect = [
        "Bob Johnson",  # Name
        "No, I need a different time",  # Decline scheduling
        "Next week would be better",  # Preferred time
        "",  # End conversation
    ]
    
    # Initial state
    state = create_test_state()
    
    # Run the workflow
    next_state = workflow.invoke(state)
    
    # Verify the workflow handled rescheduling
    assert next_state["current_step"] == END
    assert next_state["customer"]["name"] == "Bob Johnson"
    assert any("reschedule" in msg.content.lower() for msg in next_state["messages"] if isinstance(msg, AIMessage))

def test_additional_questions_flow(workflow, mock_input):
    """Test workflow with additional questions"""
    # Setup mock inputs for the conversation
    mock_input.side_effect = [
        "Carol White",  # Name
        "What type of faucet do you install?",  # Additional question
        "Yes",  # Schedule confirmation
        "",  # End conversation
    ]
    
    # Initial state
    state = create_test_state()
    
    # Run the workflow
    next_state = workflow.invoke(state)
    
    # Verify the workflow handled additional questions
    assert next_state["current_step"] == END
    assert next_state["customer"]["name"] == "Carol White"
    assert any("faucet" in msg.content.lower() for msg in next_state["messages"] if isinstance(msg, AIMessage))

def test_unclear_sentiment_retry(workflow, mock_input):
    """Test workflow with unclear responses"""
    # Setup mock inputs for the conversation
    mock_input.side_effect = [
        "David Brown",  # Name
        "Maybe",  # Unclear response
        "I guess so",  # Still unclear
        "Yes definitely",  # Clear positive
        "",  # End conversation
    ]
    
    # Initial state
    state = create_test_state()
    
    # Run the workflow
    next_state = workflow.invoke(state)
    
    # Verify the workflow handled unclear responses
    assert next_state["current_step"] == END
    assert next_state["customer"]["name"] == "David Brown"
    assert next_state["sentiment_attempts"] >= 2

def test_contractor_meeting_flow(workflow, mock_input):
    """Test workflow for existing customer checking on contractor meeting"""
    # Setup mock inputs for the conversation
    mock_input.side_effect = [
        "Yes, we met yesterday",  # Confirm meeting
        "The meeting went well",  # Additional info
        "",  # End conversation
    ]
    
    # Initial state with existing customer
    state = create_test_state()
    state["customer"]["name"] = "Charlie Davis"  # Existing customer
    
    # Run the workflow
    next_state = workflow.invoke(state)
    
    # Verify the workflow handled the meeting confirmation
    assert next_state["current_step"] == END
    assert any("meeting went well" in msg.content.lower() for msg in next_state["messages"] if isinstance(msg, HumanMessage))

def test_error_handling(workflow, mock_input):
    """Test workflow error handling"""
    # Setup mock inputs that might cause errors
    mock_input.side_effect = [
        "",  # Empty name
        "Eve Wilson",  # Valid name
        "Yes",  # Simple response
        "",  # End conversation
    ]
    
    # Initial state
    state = create_test_state()
    
    # Run the workflow
    next_state = workflow.invoke(state)
    
    # Verify the workflow handled the error and recovered
    assert next_state["current_step"] == END
    assert next_state["customer"]["name"] == "Eve Wilson"
    assert any("didn't catch your name" in msg.content.lower() for msg in next_state["messages"] if isinstance(msg, AIMessage))

@pytest.mark.asyncio
async def test_async_workflow_execution(workflow, mock_input):
    """Test asynchronous workflow execution"""
    # Setup mock inputs
    mock_input.side_effect = [
        "Frank Miller",  # Name
        "Yes",  # Schedule confirmation
        "",  # End conversation
    ]
    
    # Initial state
    state = create_test_state()
    
    # Run the workflow with custom recursion limit
    config = {"recursion_limit": 5}
    next_state = workflow.invoke(state, config=config)
    
    # Assertions
    assert next_state["customer"]["name"] == "Frank Miller"
    assert len(next_state["messages"]) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 