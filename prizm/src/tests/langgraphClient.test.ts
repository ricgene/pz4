import { callLangGraphAgent } from '../langgraphClient';

// Test cases
const testCases = [
  {
    name: "Basic greeting",
    request: {
      userId: "test-user-1",
      message: "Hello, how can you help me today?",
      context: {
        system_prompt: "You are a helpful assistant.",
        memory_context: {
          is_first_message: true
        },
        timestamp: new Date().toISOString()
      }
    }
  },
  {
    name: "Task inquiry",
    request: {
      userId: "test-user-2",
      message: "I need help with a home improvement project",
      context: {
        system_prompt: "You are a home improvement assistant.",
        memory_context: {
          user_name: "John",
          is_first_message: false
        },
        timestamp: new Date().toISOString()
      }
    }
  },
  {
    name: "Name introduction",
    request: {
      userId: "test-user-3",
      message: "My name is Alice",
      context: {
        system_prompt: "You are a friendly assistant.",
        memory_context: {
          is_name_introduction: true,
          is_first_message: true
        },
        timestamp: new Date().toISOString()
      }
    }
  }
];

// Run all test cases
async function runTests() {
  console.log("Starting LangGraph client tests...\n");

  for (const testCase of testCases) {
    console.log(`Running test: ${testCase.name}`);
    console.log("Request:", JSON.stringify(testCase.request, null, 2));
    
    try {
      const response = await callLangGraphAgent(testCase.request);
      console.log("Response:", JSON.stringify(response, null, 2));
      console.log("Test passed!\n");
    } catch (error) {
      console.error("Test failed:", error);
      console.log("\n");
    }
  }

  console.log("All tests completed!");
}

// Run the tests
runTests().catch(console.error); 