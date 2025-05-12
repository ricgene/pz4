# LangSmith Workflow Implementation

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

## Documentation

- [Memory Types](docs/README-langsmith-memory-types.md) - Detailed explanation of LangSmith memory types
- [Memory Implementation Plan](docs/MemoryImplementationPlanForLangGraph.md) - Plan for implementing memory in LangGraph
- [Test Agent Documentation](docs/read-me-test-agent.md) - Information about the test agent
- [Example Files](docs/README-note-on-example-files.md) - Documentation for example files

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

## Development Workflow

1. Run mock tests during development:
```bash
export MOCK_SENTIMENT_ANALYSIS=True
pytest tests/test_workflow2_pytest.py -v -k "not test_llm"
```

2. Test specific scenarios interactively:
```bash
python tests/test_workflow2_local.py
```

3. Before deployment, run full test suite including LLM tests:
```bash
export MOCK_SENTIMENT_ANALYSIS=False
pytest tests/test_workflow2_pytest.py -v
```

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
├── docs/                 # Documentation
│   ├── README-langsmith-memory-types.md
│   ├── MemoryImplementationPlanForLangGraph.md
│   ├── read-me-test-agent.md
│   └── README-note-on-example-files.md
├── memory/               # Memory storage
├── requirements.txt      # Dependencies
└── .env-example         # Environment variables template
```

# Test locally from file
cd ~/gitl/langpz3

See ~gitl/pz3/client-agent/README.md

poetry run python workflow2.py

# to run workflow2.py locally in studio
poetry run langgraph dev
# starts this: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024 
# then paste input data from workflow2.py file into studio input.

# incorporate query-trace-filter-out-scanned.py
poetry run python query-langgraph.py

# Test in the cloud:
Deploy:
   https://smith.langchain.com/o/fa54f251-75d3-4005-8788-376a48b2c6c0/host/deployments
   https://github.com/ricgene/gitl/langpz3

   # https://www.perplexity.ai/search/what-url-is-called-to-start-a-GXUl38JgQUSREB1WI_g5Tg

https://smith.langchain.com/studio/thread




#later, separately - let's see
poetry run test-agent-local-studio-nostream.py
