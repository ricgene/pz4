#!/usr/bin/env python
"""
Simple test script for LangSmith integration
This script tests the direct connection to LangSmith without the full 007 workflow
"""

import os
import sys
import json
from typing import Dict, Any
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys from environment
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGCHAIN_PROJECT", "007-productivity-agent")
LANGSMITH_GRAPH = "007_workflow"  # This matches the graph name in the Bond7 workflow

def test_langsmith_connection():
    """Test the connection to LangSmith"""
    print("\n=== Testing LangSmith Connection ===\n")
    
    if not LANGSMITH_API_KEY:
        print("❌ Error: LANGSMITH_API_KEY not found in environment variables")
        return False
    
    print(f"✅ Found LangSmith API key")
    print(f"✅ Project: {LANGSMITH_PROJECT}")
    print(f"✅ Graph: {LANGSMITH_GRAPH}")
    
    return True

def test_langsmith_workflow():
    """Test invoking a LangSmith workflow"""
    print("\n=== Testing LangSmith Workflow ===\n")
    
    # Prepare test input
    test_input = {
        "customer": {
            "name": "Test User",
            "email": "test@example.com",
            "phoneNumber": "555-123-4567",
            "zipCode": "94105"
        },
        "task": {
            "description": "Hello, I'm testing the LangSmith integration.",
            "category": "Test"
        },
        "vendor": {
            "name": "007 Productivity Agent",
            "email": "agent@007.example.com",
            "phoneNumber": "555-007-0007"
        },
        "memory": {
            "system_prompt": "You are 007, a personal productivity agent.",
            "user_name": "Test User",
            "is_first_message": True
        }
    }
    
    # Prepare API request
    url = f"https://api.smith.langchain.com/api/v1/projects/{LANGSMITH_PROJECT}/graphs/{LANGSMITH_GRAPH}/invoke"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LANGSMITH_API_KEY}"
    }
    
    try:
        print("📤 Sending test request to LangSmith...")
        response = requests.post(url, headers=headers, json={"input": test_input})
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Successfully received response from LangSmith:")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"\n❌ Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error calling LangSmith: {str(e)}")
        return False

def main():
    """Main function to run the tests"""
    print("\n🚀 Starting LangSmith Integration Test\n")
    
    # Test connection
    if not test_langsmith_connection():
        print("\n❌ Connection test failed. Exiting.")
        return
    
    # Test workflow
    if not test_langsmith_workflow():
        print("\n❌ Workflow test failed.")
        return
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    main() 