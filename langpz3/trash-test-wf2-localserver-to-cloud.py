#!/usr/bin/env python
"""
Simple test script for LangGraph WF2 Deployment

This script helps diagnose connection issues with your renamed workflow
by attempting to connect to both the old and new workflow names.
"""

import os
import json
import requests
from dotenv import load_dotenv
import sys
from pathlib import Path

# Load environment variables from .env file
env_path = Path("./") / '.env'
load_dotenv(env_path)

# Get API key (trying both possible environment variable names)
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
PROJECT_NAME = os.getenv("LANGCHAIN_PROJECT", "prizm-workflow-2")

def test_deployment(workflow_name):
    """Test the cloud deployment with a specific workflow name"""
    print(f"\n=== Testing Cloud Deployment for '{workflow_name}' ===\n")
    
    if not LANGSMITH_API_KEY:
        print("❌ LANGSMITH_API_KEY not found in environment variables")
        return False
    
    print(f"✅ Using API key: {LANGSMITH_API_KEY[:4]}...{LANGSMITH_API_KEY[-4:]}")
    print(f"✅ Project name: {PROJECT_NAME}")
    
    # Prepare test input (minimal valid input based on your code)
    test_input = {
        "customer": {
            "name": "Test User",
            "email": "test@example.com",
            "phoneNumber": "555-123-4567",
            "zipCode": "94105"
        },
        "task": {
            "description": "Kitchen renovation",
            "category": "Remodeling"
        },
        "vendor": {
            "name": "Dave's Plumbing",
            "email": "dave@plumbing.com",
            "phoneNumber": "555-987-6543"
        }
    }
    
    # Prepare API request
    url = f"https://api.smith.langchain.com/api/v1/projects/{PROJECT_NAME}/graphs/{workflow_name}/invoke"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LANGSMITH_API_KEY}"
    }
    
    try:
        print(f"📤 Sending test request to LangSmith at URL: {url}")
        response = requests.post(url, headers=headers, json={"input": test_input})
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Successfully received response from LangSmith:")
            print(json.dumps(result.get("output", {}), indent=2)[:500] + "...")
            return True
        else:
            print(f"\n❌ Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error calling LangSmith: {str(e)}")
        return False

def check_local_server():
    """Check if a local LangGraph server is running"""
    try:
        response = requests.get("http://127.0.0.1:2024/health")
        if response.status_code == 200:
            print("\n✅ Local LangGraph server is running")
            return True
        else:
            print("\n❌ Local LangGraph server returned unexpected status code")
            return False
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to local LangGraph server at http://127.0.0.1:2024")
        return False

def test_local_deployment(workflow_name):
    """Test the local deployment with a specific workflow name"""
    print(f"\n=== Testing Local Deployment for '{workflow_name}' ===\n")
    
    if not check_local_server():
        print("Skipping local test due to server connection issue")
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
            "category": "Remodeling"
        },
        "vendor": {
            "name": "Dave's Plumbing",
            "email": "dave@plumbing.com",
            "phoneNumber": "555-987-6543"
        }
    }
    
    # Prepare API request
    url = f"http://127.0.0.1:2024/api/v1/{workflow_name}/invoke"
    
    try:
        print(f"📤 Sending test request to local LangGraph at URL: {url}")
        response = requests.post(url, json={"input": test_input})
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Successfully received response from local LangGraph:")
            print(json.dumps(result.get("output", {}), indent=2)[:500] + "...")
            return True
        else:
            print(f"\n❌ Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error calling local LangGraph: {str(e)}")
        return False

def check_langgraph_json():
    """Check the langgraph.json file for configuration issues"""
    try:
        with open("langgraph.json", "r") as f:
            config = json.load(f)
            
        print("\n=== LangGraph Configuration ===")
        print(f"Name: {config.get('name', 'Not specified')}")
        print(f"Entrypoint: {config.get('entrypoint', 'Not specified')}")
        print(f"Project: {config.get('project', 'Not specified')}")
        
        # Check for workflow name mismatch
        if config.get('name') != "wf2" and config.get('name') == "workflow2":
            print("⚠️ WARNING: langgraph.json still uses 'workflow2' name instead of 'wf2'")
            
        return config
    except Exception as e:
        print(f"\n❌ Error reading langgraph.json: {str(e)}")
        return None

def main():
    """Main function to run the tests"""
    print("\n🚀 Starting LangGraph Deployment Tests\n")
    
    # Check configuration
    config = check_langgraph_json()
    
    # Test old workflow name
    old_name_cloud = test_deployment("workflow2")
    old_name_local = test_local_deployment("workflow2")
    
    # Test new workflow name
    new_name_cloud = test_deployment("wf2")
    new_name_local = test_local_deployment("wf2")
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Cloud deployment 'workflow2': {'✅ Successful' if old_name_cloud else '❌ Failed'}")
    print(f"Local deployment 'workflow2': {'✅ Successful' if old_name_local else '❌ Failed'}")
    print(f"Cloud deployment 'wf2': {'✅ Successful' if new_name_cloud else '❌ Failed'}")
    print(f"Local deployment 'wf2': {'✅ Successful' if new_name_local else '❌ Failed'}")
    
    # Provide instructions based on results
    print("\n=== Recommended Actions ===")
    if old_name_cloud and not new_name_cloud:
        print("1. Your deployment is still using the old name 'workflow2'.")
        print("2. Update your langgraph.json file to use 'wf2' as the name.")
        print("3. Re-deploy your application to LangSmith.")
    elif not old_name_cloud and not new_name_cloud:
        print("1. Neither workflow name is working in the cloud.")
        print("2. Check your LangSmith API key and project name.")
        print("3. Ensure you've properly deployed your application to LangSmith.")
    elif new_name_cloud:
        print("1. Your cloud deployment with the new name 'wf2' is working correctly.")
        print("2. Update any client code to use the new name.")
    
    if old_name_local and not new_name_local:
        print("3. Your local server is still using the old name 'workflow2'.")
        print("4. When running 'langgraph dev', make sure to update your local config.")
    elif not old_name_local and not new_name_local:
        print("3. Your local server isn't responding to either workflow name.")
        print("4. Make sure the local server is running with 'langgraph dev'.")
    elif new_name_local:
        print("3. Your local server is correctly configured for the new name 'wf2'.")

if __name__ == "__main__":
    main()