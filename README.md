# rsroute

### What it is
`rsroute` is a lightweight Python client for [RSRoute](https://www.github.com/ItzRustam/rsroute) — a unified gateway that routes requests across 10+ LLM providers seamlessly.

### Why it is
Instead of managing disparate SDKs, raw HTTP requests, query parameters, and custom endpoints manually for each provider, `rsroute` provides a simple, unified wrapper so you can connect to your RSRoute server with minimal code.

### Code Example
```python
from rsroute.chat_models import chatGemini

response = chatGemini(
    query="What is GitHub?",
    model="gemini-3.5-flash-lite",
    master_key="RSRoute_my_key"
)

print(response)
```

### Server
RSRoute Server repository: [https://www.github.com/ItzRustam/rsroute](https://www.github.com/ItzRustam/rsroute)

