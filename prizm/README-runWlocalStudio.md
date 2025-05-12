# Running LangGraph with Local Studio

This guide explains how to run the LangGraph server locally and interact with it through the LangChain Studio UI.

## Prerequisites

- Python 3.11
- Virtual environment with required packages
- LangGraph CLI with in-memory support

## Setup

1. Navigate to the langpz3 directory:
```bash
cd ~/gitl/4pz/langpz3
```

2. Activate the virtual environment:
```bash
source .venv/bin/activate
```

3. Install required packages if not already installed:
```bash
pip install -U "langgraph-cli[inmem]"
```

## Running the Local Server

1. Start the LangGraph development server:
```bash
langgraph dev
```

The server will start and provide:
- API endpoint: http://127.0.0.1:2024
- Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- API Documentation: http://127.0.0.1:2024/docs

## Using the Studio UI

1. Open the Studio UI in your browser:
   https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

2. Create a new thread in the Studio UI

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

## Troubleshooting

1. If you see "not found" in the browser:
   - Make sure the server is running (check terminal output)
   - Create a new thread in the Studio UI
   - Ensure you're using the correct input format

2. If the server fails to start:
   - Check that you're in the correct directory (`~/gitl/4pz/langpz3`)
   - Verify the virtual environment is activated
   - Ensure all required packages are installed

3. If you need to restart the server:
   - Press Ctrl+C to stop the current server
   - Run `langgraph dev` again

## Notes

- The local server is for development and testing only
- For production use, use LangGraph Cloud
- The server automatically watches for file changes and reloads when needed
- You can use the API endpoint (http://127.0.0.1:2024) for direct API calls 