import axios from 'axios';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Interface for the request to the langgraph deployment
interface LangGraphRequest {
  userId: string | number;
  message: string;
  context?: {
    system_prompt?: string;
    memory_context?: {
      user_name?: string;
      is_name_introduction?: boolean;
      is_first_message?: boolean;
    };
    timestamp?: string;
  };
}

// Interface for the response from the langgraph deployment
interface LangGraphResponse {
  response: string;
  error?: string;
  sentiment?: string;
  reason?: string;
}

// Get the langgraph URL from environment variables
const LANGGRAPH_URL = process.env.LANGGRAPH_URL || 'http://localhost:8000';

/**
 * Sends a message to the langgraph deployment and returns the response
 * @param request The request to send to the langgraph deployment
 * @returns The response from the langgraph deployment
 */
export async function callLangGraphAgent(request: LangGraphRequest): Promise<LangGraphResponse> {
  try {
    console.log(`Calling LangGraph agent with request:`, request);
    
    // Prepare the request body for the LangGraph agent
    const requestBody = {
      customer: {
        name: request.context?.memory_context?.user_name || `User ${request.userId}`,
        email: `user${request.userId}@example.com`,
        phoneNumber: "555-123-4567",
        zipCode: "00000"
      },
      task: {
        description: request.message,
        category: "General Inquiry"
      },
      vendor: {
        name: "PRIZM Assistant",
        email: "assistant@prizm.ai",
        phoneNumber: "555-987-6543"
      },
      // Include memory context
      memory: {
        system_prompt: request.context?.system_prompt,
        is_name_introduction: request.context?.memory_context?.is_name_introduction,
        user_name: request.context?.memory_context?.user_name
      },
      // Include any additional context
      ...request.context
    };
    
    console.log("Sending to LangGraph:", JSON.stringify(requestBody, null, 2));
    
    // Call the LangGraph agent
    const response = await axios.post(`${LANGGRAPH_URL}/api/agent`, requestBody, {
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 15000 // 15 second timeout
    });
    
    console.log("Received response from LangGraph:", response.data);
    
    // Process and return the response
    return {
      response: response.data.response || response.data.message || "I understand. How can I help you today?",
      sentiment: response.data.sentiment || "neutral",
      reason: response.data.reason || "No additional reason provided"
    };
  } catch (error) {
    console.error('Error calling LangGraph agent:', error);
    return {
      response: "I apologize, but I encountered an error processing your message.",
      error: error instanceof Error ? error.message : 'Unknown error',
      sentiment: "negative",
      reason: "Error occurred during processing"
    };
  }
}

// Example usage
async function main() {
  const request: LangGraphRequest = {
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

// Run the example if this file is executed directly
if (require.main === module) {
  main();
} 