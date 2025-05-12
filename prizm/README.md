# Prizm LangGraph Client

A TypeScript client for interacting with a LangGraph deployment.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file in the project root with the following content:
```env
# LangGraph deployment URL
LANGGRAPH_URL=http://localhost:8000

# Optional: Add your API key if required
# API_KEY=your_api_key_here
```

3. Build the TypeScript code:
```bash
npm run build
```

## Usage

The main functionality is provided by the `callLangGraphAgent` function in `src/langgraphClient.ts`. Here's an example of how to use it:

```typescript
import { callLangGraphAgent } from './src/langgraphClient';

async function example() {
  const request = {
    userId: "test-user",
    message: "Hello, how can you help me today?",
    context: {
      system_prompt: "You are a helpful assistant.",
      memory_context: {
        is_first_message: true
      },
      timestamp: new Date().toISOString()
    }
  };

  try {
    const response = await callLangGraphAgent(request);
    console.log("Response:", response);
  } catch (error) {
    console.error("Error:", error);
  }
}
```

## Development

1. Start the TypeScript compiler in watch mode:
```bash
npm run dev
```

2. Run the example:
```bash
npm run start
```

## Project Structure

- `src/langgraphClient.ts`: Main client implementation for interacting with the LangGraph deployment
- `.env`: Configuration file for environment variables
- `tsconfig.json`: TypeScript configuration
- `package.json`: Project dependencies and scripts 