# Standalone LangGraph Client Testing

This directory contains a standalone TypeScript client for testing interactions with a LangGraph deployment. The test suite includes a mock server that simulates the LangGraph deployment, allowing you to test the client without needing a real deployment.

## Project Structure

```
prizm/
├── src/
│   ├── langgraphClient.ts     # Main client implementation
│   └── tests/
│       ├── langgraphClient.test.ts  # Test cases
│       └── mockServer.ts      # Mock LangGraph server
├── package.json
└── tsconfig.json
```

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file in the project root:
```env
LANGGRAPH_URL=http://localhost:8000
```

## Running the Tests

The test suite consists of two parts:
1. A mock server that simulates the LangGraph deployment
2. Test cases that verify the client's functionality

### Running the Mock Server

In one terminal, start the mock server:
```bash
npm run mock-server
```

The server will start on port 8000 and log incoming requests and outgoing responses.

### Running the Tests

In another terminal, run the test suite:
```bash
npm test
```

## Test Cases

The test suite includes three test cases:

1. **Basic Greeting**
   - Tests a simple hello message
   - Verifies first-time interaction handling
   - Expected response includes a greeting and positive sentiment

2. **Task Inquiry**
   - Tests a project-related query
   - Includes user context (name: "John")
   - Verifies project-specific response generation

3. **Name Introduction**
   - Tests name introduction handling
   - Verifies proper greeting with user's name
   - Checks first message handling

## Mock Server Behavior

The mock server simulates different scenarios:

- **First-time interactions**: Returns a greeting with the user's name
- **Name introductions**: Acknowledges the name introduction
- **Project inquiries**: Provides project-specific responses
- **General queries**: Returns a neutral response

Each response includes:
- `response`: The main message
- `sentiment`: The emotional tone (positive/neutral/negative)
- `reason`: The context for the response

## Example Output

When running the tests, you'll see:

1. Mock server output showing:
   - Received requests with full context
   - Generated responses with sentiment and reason

2. Test output showing:
   - Test case execution
   - Request details
   - Response validation
   - Pass/fail status

## Error Handling

The mock server includes error handling for:
- Invalid requests
- Missing required fields
- Server errors

The client handles:
- Connection errors
- Timeout errors
- Invalid responses

## Development

To modify the test suite:

1. Add new test cases in `src/tests/langgraphClient.test.ts`
2. Update mock responses in `src/tests/mockServer.ts`
3. Run the tests to verify changes

## Notes

- The mock server runs on port 8000 by default
- All tests are designed to pass with the mock server
- The client is configured to work with both mock and real deployments
- Test responses are deterministic for consistent testing 