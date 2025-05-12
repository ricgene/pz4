import pytest
from workflow2 import app, WorkflowState
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os

# Test data fixtures
@pytest.fixture
def test_state():
    return {
        "customer": {
            "name": "Test User",
            "email": "test@example.com",
            "phoneNumber": "555-0123",
            "zipCode": "12345"
        },
        "task": {
            "description": "Kitchen renovation",
            "category": "Home Improvement"
        },
        "vendor": {
            "name": "Dave's Plumbing",
            "email": "dave@plumbing.com",
            "phoneNumber": "555-9876"
        }
    }

@pytest.fixture
def mock_env():
    # Store original env vars
    original_mock_responses = os.environ.get('MOCK_USER_RESPONSES')
    original_mock_sentiment = os.environ.get('MOCK_SENTIMENT_ANALYSIS')
    
    # Set test env vars
    os.environ['MOCK_USER_RESPONSES'] = 'True'
    os.environ['MOCK_SENTIMENT_ANALYSIS'] = 'True'
    
    yield
    
    # Restore original env vars
    if original_mock_responses:
        os.environ['MOCK_USER_RESPONSES'] = original_mock_responses
    else:
        del os.environ['MOCK_USER_RESPONSES']
        
    if original_mock_sentiment:
        os.environ['MOCK_SENTIMENT_ANALYSIS'] = original_mock_sentiment
    else:
        del os.environ['MOCK_SENTIMENT_ANALYSIS']

@pytest.fixture
def llm_env(mock_env):
    os.environ['MOCK_SENTIMENT_ANALYSIS'] = 'False'
    yield

def test_workflow_initialization(test_state):
    """Test that the workflow initializes correctly"""
    result = app.invoke(test_state)
    
    assert result is not None
    assert 'messages' in result
    assert len(result['messages']) > 0
    assert isinstance(result['messages'][0], SystemMessage)
    assert isinstance(result['messages'][1], AIMessage)

@pytest.mark.parametrize("response,expected_sentiment", [
    ("yes", "positive"),
    ("I'll do it tomorrow", "positive"),
    ("sounds great", "positive"),
    ("no", "negative"),
    ("I can't right now", "negative"),
    ("I'm concerned about the cost", "negative"),
    ("maybe", "unknown"),
    ("I'll think about it", "unknown"),
])
def test_mock_sentiment_analysis(test_state, mock_env, response, expected_sentiment):
    """Test sentiment analysis with mock responses"""
    # Add the test response to messages
    test_state['messages'] = [
        SystemMessage(content="Test system message"),
        AIMessage(content="Test AI message"),
        HumanMessage(content=response)
    ]
    
    result = app.invoke(test_state)
    
    assert result['sentiment'] == expected_sentiment
    assert 'reason' in result
    assert len(result['reason']) > 0

@pytest.mark.skipif(not os.getenv('OPENAI_API_KEY'), reason="OpenAI API key not found")
@pytest.mark.parametrize("response", [
    "yes",
    "no",
    "I need more time to think about it",
    "The price seems too high",
])
def test_llm_sentiment_analysis(test_state, llm_env, response):
    """Test sentiment analysis with LLM"""
    # Add the test response to messages
    test_state['messages'] = [
        SystemMessage(content="Test system message"),
        AIMessage(content="Test AI message"),
        HumanMessage(content=response)
    ]
    
    result = app.invoke(test_state)
    
    assert 'sentiment' in result
    assert result['sentiment'] in ['positive', 'negative', 'unknown']
    assert 'reason' in result
    assert len(result['reason']) > 0

def test_conversation_flow(test_state, mock_env):
    """Test the full conversation flow"""
    # Initial state
    result = app.invoke(test_state)
    assert len(result['messages']) > 0
    
    # Add a positive response
    test_state['messages'] = result['messages'] + [HumanMessage(content="yes")]
    result = app.invoke(test_state)
    assert result['sentiment'] == 'positive'
    
    # Add a negative response
    test_state['messages'] = result['messages'] + [HumanMessage(content="no")]
    result = app.invoke(test_state)
    assert result['sentiment'] == 'negative'

def test_error_handling(test_state, mock_env):
    """Test error handling with invalid input"""
    # Test with missing required fields
    invalid_state = {"customer": {}}
    with pytest.raises(ValueError):
        app.invoke(invalid_state)
    
    # Test with empty messages
    test_state['messages'] = []
    result = app.invoke(test_state)
    assert result['sentiment'] == 'unknown'

if __name__ == '__main__':
    pytest.main([__file__, '-v']) 