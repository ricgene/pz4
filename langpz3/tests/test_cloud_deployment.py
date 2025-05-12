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
    load_dotenv(env_path)
    
    # Get API key
    api_key = os.getenv('LANGSMITH_API_KEY')
    if not api_key:
        print("❌ LANGSMITH_API_KEY not found in environment variables")
        return False
    
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
        }
    }
    
    # Prepare API request
    url = "https://api.smith.langchain.com/api/v1/projects/prizm-workflow-2/graphs/workflow2/invoke"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
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

if __name__ == "__main__":
    test_cloud_deployment() 