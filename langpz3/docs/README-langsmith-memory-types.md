# LangSmith Memory Types

LangSmith/LangChain provides three main types of memory systems for maintaining conversation context and history. Here's a detailed explanation of each:

## 1. Buffer Memory

Buffer memory maintains a simple list of messages in memory, storing the entire conversation history.

### Use Cases
- Short conversations where full history is needed
- When exact message order is important
- Simple chat applications

### Example Implementation
```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Usage in conversation
memory.save_context(
    {"input": "Hi, I'm John"},
    {"output": "Hello John! How can I help you?"}
)

# Retrieve history
history = memory.load_memory_variables({})
```

## 2. Summary Memory

Summary memory maintains a running summary of the conversation, useful for long conversations where storing every message would be impractical.

### Use Cases
- Long-running conversations
- When you need to maintain context without storing every message
- Memory-efficient applications

### Example Implementation
```python
from langchain.memory import ConversationSummaryMemory
from langchain_openai import ChatOpenAI

memory = ConversationSummaryMemory(
    llm=ChatOpenAI(),
    memory_key="chat_summary",
    return_messages=True
)

# Usage in conversation
memory.save_context(
    {"input": "I need help with my project"},
    {"output": "I'd be happy to help. What kind of project?"}
)

# Retrieve summary
summary = memory.load_memory_variables({})
```

## 3. Vector Memory

Vector memory stores messages in a vector database, allowing for semantic search and retrieval of relevant past conversations.

### Use Cases
- Finding relevant past conversations
- Semantic search across conversation history
- When you need to retrieve specific information based on meaning

### Example Implementation
```python
from langchain.memory import VectorStoreMemory
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Initialize vector store
vectorstore = Chroma(
    embedding_function=OpenAIEmbeddings(),
    collection_name="conversation_memory"
)

memory = VectorStoreMemory(
    vectorstore=vectorstore,
    memory_key="vector_memory",
    return_messages=True
)

# Usage in conversation
memory.save_context(
    {"input": "What's the status of my kitchen renovation?"},
    {"output": "Your kitchen renovation is scheduled for next week."}
)

# Retrieve relevant memories
relevant_memories = memory.load_memory_variables(
    {"query": "When is my renovation?"}
)
```

## Choosing the Right Memory Type

### Use Buffer Memory when:
- You need the complete conversation history
- Message order is important
- Memory usage is not a concern
- Conversations are relatively short

### Use Summary Memory when:
- Conversations are long
- You need to maintain context without storing every message
- Memory efficiency is important
- You want a high-level overview of the conversation

### Use Vector Memory when:
- You need to search through past conversations
- Semantic similarity is important
- You want to retrieve specific information based on meaning
- You need to find relevant past interactions

## Implementation Tips

1. **Memory Key**: Always specify a unique `memory_key` for each memory instance
2. **Return Messages**: Set `return_messages=True` if you need the full message objects
3. **Memory Variables**: Use `load_memory_variables()` to retrieve stored information
4. **Context Saving**: Use `save_context()` to store new interactions

## Best Practices

1. **Memory Cleanup**: Implement periodic cleanup for buffer and vector memories
2. **Summary Updates**: Regularly update summaries in summary memory
3. **Error Handling**: Always handle cases where memory retrieval fails
4. **Memory Limits**: Set appropriate limits for buffer size or vector store capacity

## Example Integration with Workflow

```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI

# Initialize memory and chain
memory = ConversationBufferMemory(memory_key="chat_history")
llm = ChatOpenAI()
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# Use in conversation
response = conversation.predict(input="Hi, I'm John")
print(response)  # "Hello John! How can I help you?"

# Memory persists between calls
response = conversation.predict(input="Do you remember my name?")
print(response)  # "Yes, your name is John!"
``` 