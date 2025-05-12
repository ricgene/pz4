import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

// Debug logging for environment variables
console.log('Environment variables loaded:');
console.log('LANGGRAPH_URL:', process.env.LANGGRAPH_URL);
console.log('LANGCHAIN_API_KEY:', process.env.LANGCHAIN_API_KEY ? 'Present' : 'Missing');
console.log('---\n');

// Cloud endpoint URL - this should be set in your .env file
const LANGGRAPH_URL = process.env.LANGGRAPH_URL || 'https://workflow2-5-10-cb3640c24ee559b080f87a3d156740ae.us.langgraph.app';

interface CloudRequest {
  customer: {
    name: string;
    email: string;
    phoneNumber: string;
    zipCode: string;
  };
  task: {
    description: string;
    category: string;
  };
  vendor: {
    name: string;
    email: string;
    phoneNumber: string;
  };
  memory?: {
    system_prompt?: string;
    is_name_introduction?: boolean;
    user_name?: string;
  };
}

interface CloudResponse {
  response: string;
  sentiment?: string;
  reason?: string;
  error?: string;
}

async function callCloudEndpoint(request: CloudRequest): Promise<CloudResponse> {
  try {
    console.log(`Calling cloud endpoint at ${LANGGRAPH_URL}/api/agent`);
    console.log('Request:', JSON.stringify(request, null, 2));
    
    const response = await axios.post(`${LANGGRAPH_URL}/api/agent`, request, {
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.LANGCHAIN_API_KEY
      },
      timeout: 30000 // 30 second timeout for cloud requests
    });
    
    console.log('Response:', JSON.stringify(response.data, null, 2));
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('Error calling cloud endpoint:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message
      });
    } else {
      console.error('Error calling cloud endpoint:', error);
    }
    throw error;
  }
}

async function runTests() {
  console.log('Starting cloud endpoint tests...\n');
  console.log('Using endpoint:', `${LANGGRAPH_URL}/api/agent`);
  console.log('API Key present:', !!process.env.LANGCHAIN_API_KEY, '\n');

  // Test 1: Basic greeting
  try {
    console.log('Test 1: Basic greeting');
    const request1: CloudRequest = {
      customer: {
        name: 'Test User',
        email: 'test@example.com',
        phoneNumber: '555-123-4567',
        zipCode: '00000'
      },
      task: {
        description: 'Hello, how are you?',
        category: 'General Inquiry'
      },
      vendor: {
        name: 'PRIZM Assistant',
        email: 'assistant@prizm.ai',
        phoneNumber: '555-987-6543'
      },
      memory: {
        is_name_introduction: false,
        user_name: 'Test User'
      }
    };

    const response1 = await callCloudEndpoint(request1);
    console.log('Response:', response1);
    console.log('Test 1 passed!\n');
  } catch (error) {
    console.error('Test 1 failed:', error);
  }

  // Test 2: Task inquiry
  try {
    console.log('Test 2: Task inquiry');
    const request2: CloudRequest = {
      customer: {
        name: 'Test User',
        email: 'test@example.com',
        phoneNumber: '555-123-4567',
        zipCode: '00000'
      },
      task: {
        description: 'I need help with a home improvement project',
        category: 'Task Management'
      },
      vendor: {
        name: 'PRIZM Assistant',
        email: 'assistant@prizm.ai',
        phoneNumber: '555-987-6543'
      },
      memory: {
        is_name_introduction: false,
        user_name: 'Test User'
      }
    };

    const response2 = await callCloudEndpoint(request2);
    console.log('Response:', response2);
    console.log('Test 2 passed!\n');
  } catch (error) {
    console.error('Test 2 failed:', error);
  }

  // Test 3: Name introduction
  try {
    console.log('Test 3: Name introduction');
    const request3: CloudRequest = {
      customer: {
        name: 'Alice',
        email: 'alice@example.com',
        phoneNumber: '555-123-4567',
        zipCode: '00000'
      },
      task: {
        description: 'My name is Alice',
        category: 'General Inquiry'
      },
      vendor: {
        name: 'PRIZM Assistant',
        email: 'assistant@prizm.ai',
        phoneNumber: '555-987-6543'
      },
      memory: {
        is_name_introduction: true,
        user_name: 'Alice'
      }
    };

    const response3 = await callCloudEndpoint(request3);
    console.log('Response:', response3);
    console.log('Test 3 passed!\n');
  } catch (error) {
    console.error('Test 3 failed:', error);
  }
}

// Run the tests
runTests().catch(console.error); 