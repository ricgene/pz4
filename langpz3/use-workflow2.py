import requests
import json

# Your LangSmith API key
api_key = "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"

# Your workflow data
data = {
    "customer": {
        "name": "John Smith",
        "email": "john.smith@example.com",
        "phoneNumber": "555-123-4567",
        "zipCode": "94105"
    },
    "task": {
        "description": "Kitchen renovation",
        "category": "Remodeling"
    },
    "vendor": {
        "name": "Bay Area Remodelers",
        "email": "contact@bayarearemodelers.com",
        "phoneNumber": "555-987-6543"
    }
}

# Make the API request
headers = {
    "Content-Type": "application/json",
    "x-api-key": api_key
}

response = requests.post(
    "https://api.smith.langchain.com/projects/b047ac5c-7bbc-4043-a436-3fe99b5d119b/graphs/workflow2/invoke",
    headers=headers,
    json=data
)

# Process the response
if response.status_code == 200:
    result = response.json()
    print(json.dumps(result, indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")
