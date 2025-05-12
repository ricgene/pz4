# Setting Up and Testing the 007 Productivity Agent

Follow these steps to set up and test the 007 productivity agent locally.

## Prerequisites

- Python 3.11 or newer
- Poetry (for dependency management)

## Setup Steps

1. **Clone the repository** (if you haven't already)

2. **Set up environment variables**
   Copy the `.env-example` file to `.env` and fill in your API keys:
   ```bash
   cp .env-example .env
   ```
   Then edit the `.env` file to add your OpenAI API key.

3. **Install dependencies**
   ```bash
   poetry install
   ```

4. **Save the complete workflow implementation**
   Save the provided `complete_007_workflow.py` file to the `agent` directory:
   ```bash
   # Create the file
   touch agent/complete_007_workflow.py
   
   # Open it in your editor
   # Then paste the code from the "Complete 007-workflow.py" artifact
   ```

5. **Save the test script**
   Save the `test-007-agent.py` file to the project root directory.

## Running the Agent Locally

You can run the agent directly:

```bash
poetry run python agent/complete_007_workflow.py
```

Or use the test script:

```bash
poetry run python test-007-agent.py
```

## Testing in LangGraph Studio

To run the agent in LangGraph Studio:

1. Start the LangGraph development server:
   ```bash
   poetry run langgraph dev
   ```

2. Open the Studio URL: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

3. Create a new thread and initialize with an empty input (just `{}`).

4. Interact with the agent through the Studio interface.

## Deploying to LangSmith

Update the `langgraph.json` file to include your new agent:

```json
{
    "dependencies": ["."],
    "graphs": {
        "contractor_workflow2": "./agent/workflow2.py:app",
        "productivity_agent": "./agent/complete_007_workflow.py:app"
    },
    "env": ".env",
    "python_version": "3.11"
}
```

Then deploy following the instructions in the README.md.