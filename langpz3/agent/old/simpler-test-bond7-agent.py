# debug-test-agent.py
# A debug test script for the 007 productivity agent

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_env():
    """Check if required environment variables are set"""
    required_vars = ["OPENAI_API_KEY"] 
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("\n⚠️  Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in a .env file or in your environment.")
        print("You can use .env-example as a template.")
        return False
    
    return True

def main():
    """Main function to run the test"""
    print("\n🚀 Starting 007 Productivity Agent Debug Test\n")
    
    # Check environment variables
    if not check_env():
        return
    
    # Save the original debug workflowbond7.py to debug_workflowbond7.py
    source_file = os.path.join(os.path.dirname(__file__), "noopenai_workflowbond7.py")
    
    print(f"Running debug agent from: {source_file}")
    
    # Import the agent module
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        # Try to dynamically import the module
        import importlib.util
        spec = importlib.util.spec_from_file_location("debug_agent", source_file)
        debug_agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(debug_agent)
        
        # Run the agent's main function
        debug_agent.main()
    except Exception as e:
        print(f"\n❌ Error running debug agent: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()