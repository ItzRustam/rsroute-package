# rsroute

### What it is
`rsroute` is a lightweight Python client for [RSRoute](https://www.github.com/ItzRustam/rsroute) — a unified gateway that routes requests across 10+ LLM providers seamlessly.

### Why it is
Instead of managing disparate SDKs, raw HTTP requests, query parameters, and custom endpoints manually for each provider, `rsroute` provides a simple, unified wrapper so you can connect to your RSRoute server with minimal code.

### Code Example - ChatModel
```python
from rsroute.chat_models import ChatGemini

Model = ChatGemini(
    model="gemini-3.5-flash-lite",
    rsroute_url="http://0.0.0.0:8000", # your URL always default to this.
)

response = Model.invoke(query="What is GitHub?")
print(response)
```

### Code Example - Agents
```python
from rsroute.agents import GeminiAgent

agent = GeminiAgents(
    tools=[web_search], # your tools
    max_tool_calls=12 # Default to 10
)

response = agent.invoke(query="Latest News of GPT-6 Astra")
print(response)
```

### Feature
* automatic `master_key` loading from .env
* proper request handling
* Agentic power

### Valid `.env` name
Any of the following variable names can be used in your `.env` file:
* `rsroute_token` (or `RSROUTE_TOKEN`)
* `master_key` (or `MASTER_KEY`)
* `rsroute_key` (or `RSROUTE_KEY`)
* `rsroute_master_key` (or `RSROUTE_MASTER_KEY`)


### Server
RSRoute Server repository: [https://www.github.com/ItzRustam/rsroute](https://www.github.com/ItzRustam/rsroute)

