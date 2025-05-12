more claude project directions:
- I am using bash.  I am using pip an requirements.txt, not poetry,
- I am using a venv ( 3.11 )
- my agent graph is in 007-workflow.py


# Contractor Workflow

A LangGraph workflow for connecting customers with vendors based on sentiment analysis.

## Environment Setup

This project requires Python 3.11 and uses a virtual environment for dependency management.

# Agent Implementation

## Setup

1. Create and activate virtual environment:
```bash
python -m venv .venv_py311
source .venv_py311/bin/activate  # On Windows: .venv_py311\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env-example` to `.env` and add your API keys:
```bash
cp .env-example .env
```

## Testing

### Development Mode (Mock Responses)
```bash
export MOCK_SENTIMENT_ANALYSIS=True
pytest tests/test_workflow2_pytest.py -v -k "not test_llm"
```

### Production Mode (Real LLM)
```bash
export MOCK_SENTIMENT_ANALYSIS=False
pytest tests/test_workflow2_pytest.py -v
```

### Interactive Testing
```bash
python tests/test_workflow2_local.py
```

## Cloud Deployment

Deploy to LangSmith:
1. Visit: https://smith.langchain.com/o/fa54f251-75d3-4005-8788-376a48b2c6c0/host/deployments
2. Connect to repository: https://github.com/ricgene/langpz3

## Local Studio Testing

Run workflow locally in LangSmith studio:
```bash
langgraph dev
```
This starts: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

## Query Testing
```bash
python tests/query-langgraph.py
```

## Environment Variables

- `MOCK_USER_RESPONSES`: When True, automatically generates user responses
- `MOCK_SENTIMENT_ANALYSIS`: When True, uses rule-based sentiment analysis instead of LLM
- `OPENAI_API_KEY`: Required when `MOCK_SENTIMENT_ANALYSIS` is False

## Project Structure

```
.
├── agent/                 # Main workflow implementation
│   ├── workflow2.py      # Current workflow implementation
│   └── old/             # Deprecated workflow versions
├── tests/                # All test files
│   ├── test_workflow2_pytest.py    # Automated tests
│   ├── test_workflow2_local.py     # Interactive testing
│   ├── query-langgraph.py          # Query testing
│   └── test-agent-local-studio-nostream.py  # Studio testing
├── memory/               # Memory storage
├── requirements.txt      # Dependencies
└── .env-example         # Environment variables template
```

## Features

- Customer and vendor management
- Task processing
- Sentiment analysis
- Conversation tracking
- State management
- Error handling

## Running the Workflow

### Local Development
```bash
# Activate the virtual environment
source .venv_py311/bin/activate

# Run the latest workflow
python agent/workflow_fixed.py
```

### LangSmith Studio
```bash
# Start LangSmith Studio locally
langgraph dev

# Access Studio at: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

## Environment Variables

See `.env-example` for required environment variables.

## Deployment

This project is designed to be deployed to LangSmith.

### Cloud Deployment
- Deployment URL: https://smith.langchain.com/o/fa54f251-75d3-4005-8788-376a48b2c6c0/host/deployments
- Repository: https://github.com/ricgene/langpz3

## Testing

### Development Mode (Mock Responses)
```bash
export MOCK_SENTIMENT_ANALYSIS=True
pytest test_workflow2_pytest.py -v -k "not test_llm"
```

### Production Mode (Real LLM)
```bash
export MOCK_SENTIMENT_ANALYSIS=False
pytest test_workflow2_pytest.py -v
```

### Interactive Testing
```bash
python test_workflow2_local.py
```

## Query Testing
```bash
python query-langgraph.py
```

## Notes

- The project uses pip and requirements.txt for dependency management
- All development should be done in the Python 3.11 virtual environment
- The latest workflow implementation is in `workflow_fixed.py`
- Previous workflow versions are kept for reference but will be deprecated

# incorporate query-trace-filter-out-scanned.py
poetry run python query-langgraph.py

# Test in the cloud:
Deploy:
   https://smith.langchain.com/o/fa54f251-75d3-4005-8788-376a48b2c6c0/host/deployments
   https://github.com/ricgene/langpz3

https://smith.langchain.com/studio/thread


#later, separately - let's see
poetry run test-agent-local-studio-nostream.py