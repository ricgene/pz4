import express, { Request, Response } from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';

const app = express();
const port = 8000;

// Enable CORS and JSON parsing
app.use(cors());
app.use(bodyParser.json());

// Define types for our request and response
interface MockRequest {
  task: {
    description: string;
    category: string;
  };
  customer: {
    name: string;
    email: string;
    phoneNumber: string;
    zipCode: string;
  };
  memory_context?: {
    is_first_message?: boolean;
    user_name?: string;
  };
  memory?: {
    user_name?: string;
  };
}

interface MockResponse {
  response: string;
  sentiment: string;
  reason: string;
  error?: string;
}

// Mock response generator
function generateMockResponse(request: MockRequest): MockResponse {
  const message = request.task.description.toLowerCase();
  const isFirstMessage = request.memory_context?.is_first_message;
  const userName = request.memory?.user_name || request.customer.name;

  // Generate different responses based on the message content
  if (isFirstMessage) {
    return {
      response: `Hello${userName ? ' ' + userName : ''}! I'm your AI assistant. How can I help you today?`,
      sentiment: "positive",
      reason: "First interaction greeting"
    };
  }

  if (message.includes('name')) {
    return {
      response: `Nice to meet you, ${userName}! How can I assist you today?`,
      sentiment: "positive",
      reason: "Name introduction"
    };
  }

  if (message.includes('help') || message.includes('project')) {
    return {
      response: `I'd be happy to help you with your project. Could you provide more details about what you're looking to accomplish?`,
      sentiment: "positive",
      reason: "Project inquiry"
    };
  }

  // Default response
  return {
    response: "I understand. How can I help you with that?",
    sentiment: "neutral",
    reason: "General inquiry"
  };
}

// Main endpoint
app.post('/api/agent', (req: Request<{}, {}, MockRequest>, res: Response) => {
  console.log('Received request:', JSON.stringify(req.body, null, 2));
  
  try {
    const response = generateMockResponse(req.body);
    console.log('Sending response:', JSON.stringify(response, null, 2));
    res.json(response);
  } catch (error) {
    console.error('Error processing request:', error);
    res.status(500).json({
      response: "I apologize, but I encountered an error processing your message.",
      error: error instanceof Error ? error.message : 'Unknown error',
      sentiment: "negative",
      reason: "Error occurred during processing"
    });
  }
});

// Health check endpoint
app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok' });
});

// Start the server
app.listen(port, () => {
  console.log(`Mock LangGraph server running at http://localhost:${port}`);
}); 