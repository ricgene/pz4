# Running LangGraph with Cloud Studio

This guide explains how to run the LangGraph workflow against the cloud version using LangChain Studio.

## Prerequisites

- Python 3.11
- Virtual environment with required packages
- LangSmith API key
- Access to LangChain Studio

## Setup

1. Navigate to the langpz3 directory:
```bash
cd ~/gitl/4pz/langpz3
```

2. Activate the virtual environment:
```bash
source .venv/bin/activate
```

3. Set up your environment variables:
```bash
# Copy the example env file if you haven't already
cp .env-example .env

# Edit .env to add your LangSmith API key
# LANGSMITH_API_KEY=your_api_key_here
```

## Deploying to Cloud

1. Visit the LangSmith deployment page:
   https://smith.langchain.com/o/fa54f251-75d3-4005-8788-376a48b2c6c0/host/deployments

2. Connect to the repository:
   https://github.com/ricgene/langpz3

3. The deployment will use the configuration from `langgraph.json`:
```json
{
    "name": "workflow2",
    "description": "Customer-vendor interaction workflow with sentiment analysis",
    "entrypoint": "agent/workflow2.py",
    "project": "prizm-workflow-2",
    "python_version": "3.11",
    "graphs": {
       "workflow2": "./agent/workflow2.py:app"
    }
}
```

## Using the Cloud Studio

1. Open LangChain Studio:
   https://smith.langchain.com/studio

2. Create a new thread

3. The workflow expects input in the following format:
```json
{
    "customer": {
        "name": "Test User",
        "email": "test@example.com",
        "phoneNumber": "555-123-4567",
        "zipCode": "94105"
    },
    "task": {
        "description": "Your task description here",
        "category": "Task Category"
    },
    "vendor": {
        "name": "Vendor Name",
        "email": "vendor@example.com",
        "phoneNumber": "555-987-6543"
    }
}
```

## Testing the Cloud Deployment

You can test the cloud deployment using the provided test script:
```bash
python tests/query-langgraph.py
```

## Troubleshooting

1. If you see deployment errors:
   - Check your LangSmith API key
   - Verify the repository connection
   - Ensure all required files are in the correct locations

2. If you see runtime errors:
   - Check the logs in LangChain Studio
   - Verify the input format matches the expected schema
   - Ensure all environment variables are set correctly

## Notes

- The cloud version is suitable for production use
- You can monitor runs and debug issues through the Studio UI
- The cloud version provides better scalability and reliability
- You can use the API endpoint for direct API calls to the cloud deployment 