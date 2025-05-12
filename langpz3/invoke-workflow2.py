from langsmith import Client

api_key = "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"
your_project_id = "b047ac5c-7bbc-4043-a436-3fe99b5d119b"

client = Client(api_key="your_key")
result = client.invoke_graph(project_id="your_project_id", graph_name="workflow2", input={"input": "Your query"})