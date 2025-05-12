# Testing Memory Persistence Locally

This document explains how to test the memory persistence functionality of the Bond7 agent.

## Prerequisites

1. Python 3.11 or higher
2. Virtual environment with required packages:
   ```bash
   python -m venv .venv_py311
   source .venv_py311/bin/activate
   pip install langchain-core python-dotenv
   ```

3. OpenAI API key in `.env` file:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Running the Test

1. Activate the virtual environment:
   ```bash
   source .venv_py311/bin/activate
   ```

2. Run the test script:
   ```bash
   python test_memory.py
   ```

## What the Test Does

The test script performs the following steps:

1. **First Interaction**
   - Initializes the agent with a test user email
   - Simulates a name introduction conversation
   - Verifies that the name is properly stored in memory

2. **Second Interaction**
   - Asks the agent to recall the user's name
   - Verifies that the name is correctly retrieved from memory

3. **Persistence Test**
   - Creates a new agent instance
   - Verifies that the memory is loaded from the saved file
   - Confirms that the name is still remembered

## Expected Output

The test should show:
- Successful environment variable loading
- Name extraction and storage
- Memory persistence between sessions
- Correct name recall in responses

## Memory Storage

The memory is stored in a `memory` directory with files named:
```
memory/{user_email}_memory.json
```

Each memory file contains:
- User memory (name, preferences, etc.)
- Entity memory (structured information)
- Conversation memory (message history)

## Troubleshooting

If you encounter issues:
1. Check that the `.env` file exists and contains the OpenAI API key
2. Verify that the virtual environment is activated
3. Ensure all required packages are installed
4. Check the `memory` directory for created files 