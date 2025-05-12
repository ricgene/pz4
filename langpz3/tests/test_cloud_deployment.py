#!/usr/bin/env python
"""
Test script for cloud deployment of workflow2
"""

import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

def test_cloud_deployment():
    """Test the cloud deployment of workflow2"""
    print("\n=== Testing Cloud Deployment ===\n")
    
    # Load environment variables
    env_path = Path(__file__).parent.parent / '.env'
    print(f"Looking for .env file at: {env_path}")
    load_dotenv(env_path)
    
    # Get API key
    api_key = os.getenv('LANGSMITH_API_KEY')
    if not api_key:
        print("❌ LANGSMITH_API_KEY not found in environment variables")
        return False
    print("✅ LANGSMITH_API_KEY found")
    
    # Print other important environment variables (without showing values)
    print("\nEnvironment variables found:")
    for var in ['LANGCHAIN_API_KEY', 'OPENAI_API_KEY', 'LANGCHAIN_PROJECT']:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is not set")
    
    # Prepare test input
    test_input = {
        "customer": {
            "name": "Test User",
            "email": "test@example.com",
            "phoneNumber": "555-123-4567",
            "zipCode": "94105"
        },
        "task": {
            "description": "Kitchen renovation",
            "category": "Home Improvement"
        },
        "vendor": {
            "name": "Dave's Plumbing",
            "email": "dave@plumbing.com",
            "phoneNumber": "555-987-6543"
        },
        "messages": [],
        "sentiment": "",
        "reason": "",
        "current_step": "validate",
        "sentiment_attempts": 0,
        "summary": ""
    }
    
    # Prepare API request
    url = "https://wf2-07cd4d03c5095acfa03b80a9769e007f.us.langgraph.app"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }
    
    try:
        print("\n📤 Sending test request to LangSmith...")
        print(f"URL: {url}")
        response = requests.post(url, headers=headers, json=test_input)
        
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

if __name__ == "__main__":
    test_cloud_deployment() 