# RSRoute Endpoints & Parameter Reference

> **Target Audience**: AI models, code generators, and automated routing agents.  
> **Purpose**: Formal specification of all HTTP endpoints, parameter schemas, validation rules, authentication requirements, and return formats for the RSRoute API service and underlying provider estimators.

---

## 1. System Architecture Overview

RSRoute is a FastAPI-based AI proxy service and model wrapper built on top of LangChain. It provides standardized HTTP endpoints and Python classes for interacting with multiple LLM providers:
- **Google Gemini** (`langchain-google-genai`)
- **MistralAI** (`langchain-mistralai`)
- **Groq** (`langchain-groq`)
- **OpenRouter** (`langchain-openai`)
- **OpenAI** (`langchain-openai`)

### Core File Structure
- `app/server/root.py`: Root endpoint (`GET /`) describing active routes and service metadata.
- `app/server/gemini_route.py`: Router for Gemini endpoints (`/v1/gemini/...`).
- `app/server/mistral_route.py`: Router for MistralAI endpoints (`/v1/mistral/...`).
- `app/server/groq_route.py`: Router for Groq endpoints (`/v1/groq/...`).
- `app/server/openrouter_route.py`: Router for OpenRouter endpoints (`/v1/openrouter/...`).
- `app/server/openai_route.py`: Router for OpenAI endpoints (`/v1/openai/...`).
- `app/server/tools.py`: Response formatting helpers (`ResponseTemplate`, `ChatTemplate`, `AgentTemplate`, `convertResponse`, `convertAgentResponse`, `get_org_id`, `PARAMS_INFO`).
- `app/auth.py`: Authentication utilities (`auth_exits()`, `auth(master_key)`).
- `app/defaults.py`: System-wide defaults (`DEFAULT_GEMINI_MODEL`, `DEFAULT_MISTRAL_MODEL`, `DEFAULT_GROQ_MODEL`, `DEFAULT_OPENROUTER_MODEL`, `OPENAI_DEFAULT_MODEL`, `TEMPERATURE`, `MAX_TOKENS`, `TIMEOUT`, `MAX_RETRIES`, `QUERY`).
- `app/providers/base.py`: Abstract estimators (`BaseChatModel`, `BaseAgentModel`).
- `app/providers/gemini_client.py`: `ChatGemini`, `GeminiAgent`.
- `app/providers/mistral_client.py`: `ChatMistralAI` (alias `MistralAI`), `MistralAgent`.
- `app/providers/groq_client.py`: `ChatGroq`, `GroqAgent`.
- `app/providers/openrouter_client.py`: `ChatOpenRouter`, `OpenRouterAgent`, `ChatOpenRouterAgent`.
- `app/providers/openai_client.py`: `ChatOpenAI`, `OpenAIAgent`, `ChatOpenAIAgent`.

---

## 2. Authentication & Credential Specification

Authentication is globally controlled by the environment variable `ENABLE_AUTH`:
- When `ENABLE_AUTH="true"` (case-insensitive):
  - Every `/chat` and `/agent` request requires a valid `master_key` in the request body.
  - The `master_key` **must start with the prefix `RSRoute_`**.
  - The `master_key` must match `RSRoute_MASTER_KEY` defined in `.env`.
  - If validation fails, HTTP status `200` is returned with `login: false` and `content: "Authentication Failed"`.
- When `ENABLE_AUTH="false"` or omitted:
  - Authentication checks are bypassed; `auth: false` is returned in the response.

### Provider API Keys
Provider-specific API keys must be set in the server's environment:
- `GOOGLE_API_KEY`: Required for Gemini endpoints.
- `MISTRAL_API_KEY`: Required for MistralAI endpoints.
- `GROQ_API_KEY`: Required for Groq endpoints.
- `OPENROUTER_API_KEY`: Required for OpenRouter endpoints.
- `OPENAI_API_KEY`: Required for OpenAI endpoints.

If a provider API key is missing from `.env`, the endpoint returns HTTP `200` with `content: "Invalid Request"` and an error message identifying the missing key.

### OpenAI Organization ID Specification
OpenAI endpoints require an organization identifier:
- Parameter: `organization_id` (or alias `org_id`). Defaults to `None` in request body.
- When `None` or omitted from request body, the server automatically executes `get_org_id()`, which scans `.env` for:
  `org_id`, `ORG_ID`, `organization_id`, `ORGANIZATION_ID`, `openai_org_id`, `OPENAI_ORG_ID`.
- If no Organization ID is found in the request body or `.env`, the endpoint returns HTTP `200` with:
  - `content: "Invalid Request"`
  - `error: "No OpenAI Organization ID Found, try to edit `.env`"`

---

## 3. Endpoints Matrix

| Route Path | HTTP Method | Route Type | Tool Binding Support | Associated Provider Class |
| :--- | :--- | :--- | :--- | :--- |
| `/` | `GET` | Service Index | No | N/A |
| `/v1/gemini/chat` | `POST` | Standard Chat | No | `ChatGemini` |
| `/v1/gemini/agent` | `POST` | Agentic (Tool Use) | **Yes** (`tools_info`) | `GeminiAgent` |
| `/v1/gemini/parameters` / `/parameter` | `GET` | Parameter Info | N/A | N/A |
| `/v1/mistral/chat` | `POST` | Standard Chat | No | `ChatMistralAI` / `MistralAI` |
| `/v1/mistral/agent` | `POST` | Agentic (Tool Use) | **Yes** (`tools_info`) | `MistralAgent` |
| `/v1/mistral/parameters` / `/parameter` | `GET` | Parameter Info | N/A | N/A |
| `/v1/groq/chat` | `POST` | Standard Chat | No | `ChatGroq` |
| `/v1/groq/agent` | `POST` | Agentic (Tool Use) | **Yes** (`tools_info`) | `GroqAgent` |
| `/v1/groq/parameters` / `/parameter` | `GET` | Parameter Info | N/A | N/A |
| `/v1/openrouter/chat` | `POST` | Standard Chat | No | `ChatOpenRouter` |
| `/v1/openrouter/agent` | `POST` | Agentic (Tool Use) | **Yes** (`tools_info`) | `OpenRouterAgent` |
| `/v1/openrouter/parameters` / `/parameter` | `GET` | Parameter Info | N/A | N/A |
| `/v1/openai/chat` | `POST` | Standard Chat | No | `ChatOpenAI` |
| `/v1/openai/agent` | `POST` | Agentic (Tool Use) | **Yes** (`tools_info`) | `OpenAIAgent` |
| `/v1/openai/parameters` / `/parameter` | `GET` | Parameter Info | N/A | N/A |

---

## 4. Parameter Specification

All `POST` endpoints accept a JSON body (`Content-Type: application/json`).

### 4.1 Common Parameters Across Providers

| Field Name | Type | Required | Default | Description & Validation |
| :--- | :--- | :--- | :--- | :--- |
| `query` | `string` \| `array` | Required | `"Explain Space-Time Theory in 50 Words."` | The prompt or conversational input. Converted internally to `[query]` list if passed as string. Cannot be `null`. |
| `master_key` | `string` | Conditional | `""` | Required if `ENABLE_AUTH="true"`. Must begin with `RSRoute_`. |
| `temperature` | `float` | Optional | `0.7` | Sampling randomness between `0.0` and `2.0` (`0.0` to `1.0` recommended). |
| `max_tokens` | `integer` | Optional | `4096` | Upper bound on tokens generated in response. |
| `max_retries` | `integer` | Optional | `2` | Maximum automated retry attempts on request failure. |
| `end_point` | `string` \| `null` | Optional | `null` | Custom base URL for proxies or private API gateways. |

---

### 4.2 Provider-Specific Parameter Differences

#### Google Gemini (`/v1/gemini/chat` & `/v1/gemini/agent`)
| Parameter | Type | Default | Details |
| :--- | :--- | :--- | :--- |
| `model` | `string` | `"gemini-3.5-flash-lite"` | Target Gemini model name (`DEFAULT_GEMINI_MODEL`). |
| `top_p` | `float` | `1.0` | Nucleus sampling probability boundary (`0.0` to `1.0`). |
| `thinking_level` | `string` \| `null` | `null` | Reasoning depth for Gemini 3+ models (e.g. `"low"`, `"medium"`, `"high"`). |
| `thinking_budget` | `integer` \| `null` | `null` | Explicit token budget for internal reasoning / chain-of-thought. |

#### MistralAI (`/v1/mistral/chat` & `/v1/mistral/agent`)
| Parameter | Type | Default | Details |
| :--- | :--- | :--- | :--- |
| `model` | `string` | `"mistral-small-2603"` | Target Mistral model name (`DEFAULT_MISTRAL_MODEL`). |
| `top_p` | `float` | `1.0` | Nucleus sampling probability boundary (`0.0` to `1.0`). |

#### Groq (`/v1/groq/chat` & `/v1/groq/agent`)
| Parameter | Type | Default | Details |
| :--- | :--- | :--- | :--- |
| `model` | `string` | `"openai/gpt-oss-120b"` | Target Groq model name (`DEFAULT_GROQ_MODEL`). |
| `top_p` | N/A | **Not Supported** | Excluded from Groq endpoints and parameter schema. |

#### OpenRouter (`/v1/openrouter/chat` & `/v1/openrouter/agent`)
| Parameter | Type | Default | Details |
| :--- | :--- | :--- | :--- |
| `model` | `string` | `"deepseek/deepseek-v4.1-flash"` | Target OpenRouter model name (`DEFAULT_OPENROUTER_MODEL`). |
| `top_p` | N/A | **Not Supported** | Excluded from OpenRouter endpoints and parameter schema. |
| `app_title` | `string` | `"RSRoute"` | Application title for OpenRouter rankings. |
| `app_url` | `string` | `"https://www.rsroute.freedev.app/"` | Application URL for OpenRouter rankings. |
| `app_categories` | `List[str]` \| `null` | `null` | List of category strings for OpenRouter rankings. |
| `providers` | `dict` \| `null` | `null` | Provider preference dictionary (e.g. `{"order": ["OpenAI"]}`). |

#### OpenAI (`/v1/openai/chat` & `/v1/openai/agent`)
| Parameter | Type | Default | Details |
| :--- | :--- | :--- | :--- |
| `model` | `string` | `"gpt-6-luna"` | Target OpenAI model name (`OPENAI_DEFAULT_MODEL`). |
| `top_p` | N/A | **Not Supported** | Excluded from OpenAI endpoints and parameter schema. |
| `timeout` | `integer` | `60` | Network request timeout in seconds (`TIMEOUT`). |
| `use_response_api` | `boolean` | `false` | Whether to use the OpenAI Responses API instead of Chat Completions. |
| `organization_id` | `string` \| `null` | `null` | OpenAI organization identifier. Automatically picked from `.env` via `get_org_id()` if `null`. |
| `org_id` | `string` \| `null` | `null` | Alias for `organization_id`. |

---

### 4.3 Agent Endpoint Parameter: `tools_info`

The `/agent` endpoints (`/v1/gemini/agent`, `/v1/mistral/agent`, `/v1/groq/agent`, `/v1/openrouter/agent`, `/v1/openai/agent`) accept tool declarations in `tools_info`:

- **Type**: `List[Dict[str, str]]`
- **Required**: Required when invoking an agent with bound tools.
- **Validation Rules**:
  - Must not be `None` (raises `InvalidRequest: No Tool given to Agent Edition`).
  - Must be a `list` (raises `InvalidRequest: Tools must follow the order. [{'name' : 'name of tool', 'description': 'description of tool'}]`).
  - Must not be empty (raises `InvalidRequest: No tool provided`).
  - Each item in the list must be a `dict` with both `"name"` and `"description"` string keys (raises `InvalidRequest: Give proper tool functioning name and description`).
- **Internal Mechanism**:
  - The server transforms each dictionary into a LangChain `StructuredTool` stub using `_create_fake_tools`.
  - The tools are bound to the model via `.bind_tools(tools=created_tools)`.
  - When the model determines tool invocation is necessary, tool calls are returned in the response payload's `tool_calls` field.

#### Example `tools_info` Schema:
```json
[
  {
    "name": "web_search",
    "description": "Performs web searches using DuckDuckGo/DDGS to return recent information."
  },
  {
    "name": "calculator",
    "description": "Evaluates mathematical expressions."
  }
]
```

---

## 5. Parameter Info Endpoints (`GET /parameters`)

Each provider exposes `GET /v1/<provider>/parameters` (with `/v1/<provider>/parameter` as alias):

### 5.1 Gemini: `GET /v1/gemini/parameters`
```json
{
  "query": "Input to Model",
  "master_key": "rsroute key, mandatory to send response, change it in `.env`",
  "model": "Model name",
  "temperature": "Model creativity scale from 0.0 to 1.0 default is 0.7. Mid-Creative",
  "max_tokens": "Maximum Tokens To generate in each request",
  "max_retries": "Maximum automated retry attempts on request failure (default: 2)",
  "top_p": "Nucleus sampling token selection boundary (0.0 to 1.0)",
  "end_point": "Custom url to connect to model.",
  "tools_info": "Bind Your Tool. (only in `/agent` mode)",
  "tools_info_example (not a parameter)": "[{\"name\": \"tool_name\", \"description\": \"tool_description\"}, {\"name\": \"tool2_name\", \"description\": \"description of tool2\"}]",
  "thinking_budget": " configure the token limits for reasoning and chain-of-thought processing in supported Google Gemini models",
  "thinking_level": " parameter allows you to control the depth of reasoning tokens that Gemini 3+ models generate before producing a final answer."
}
```

### 5.2 Mistral: `GET /v1/mistral/parameters`
```json
{
  "query": "Input to Model",
  "master_key": "rsroute key, mandatory to send response, change it in `.env`",
  "model": "Model name",
  "temperature": "Model creativity scale from 0.0 to 1.0 default is 0.7. Mid-Creative",
  "max_tokens": "Maximum Tokens To generate in each request",
  "max_retries": "Maximum automated retry attempts on request failure (default: 2)",
  "top_p": "Nucleus sampling token selection boundary (0.0 to 1.0)",
  "end_point": "Custom url to connect to model.",
  "tools_info": "Bind Your Tool. (only in `/agent` mode)",
  "tools_info_example (not a parameter)": "[{\"name\": \"tool_name\", \"description\": \"tool_description\"}, {\"name\": \"tool2_name\", \"description\": \"description of tool2\"}]"
}
```

### 5.3 Groq: `GET /v1/groq/parameters`
```json
{
  "query": "Input to Model",
  "master_key": "rsroute key, mandatory to send response, change it in `.env`",
  "model": "Model name, default is openai/gpt-oss-120b",
  "temperature": "Model creativity scale from 0.0 to 1.0 default is 0.7. Mid-Creative",
  "max_tokens": "Maximum Tokens To generate in each request",
  "max_retries": "Maximum automated retry attempts on request failure (default: 2)",
  "end_point": "Custom url to connect to model.",
  "tools_info": "Bind Your Tool. (only in `/agent` mode)",
  "tools_info_example (not a parameter)": "[{\"name\": \"tool_name\", \"description\": \"tool_description\"}, {\"name\": \"tool2_name\", \"description\": \"description of tool2\"}]"
}
```

### 5.4 OpenRouter: `GET /v1/openrouter/parameters`
```json
{
  "query": "Input to Model",
  "master_key": "rsroute key, mandatory to send response, change it in `.env`",
  "model": "Model name, default is deepseek/deepseek-v4.1-flash",
  "temperature": "Sampling temperature from 0.0 to 2.0, default is 0.7",
  "max_tokens": "Maximum tokens to generate in each request, default is 4096",
  "max_retries": "Maximum automated retry attempts on request failure (default: 2)",
  "end_point": "Custom url to connect to model.",
  "tools_info": "Bind Your Tool. (only in `/agent` mode)",
  "tools_info_example (not a parameter)": "[{\"name\": \"tool_name\", \"description\": \"tool_description\"}, {\"name\": \"tool2_name\", \"description\": \"description of tool2\"}]",
  "app_title": "Application title for OpenRouter rankings (default: 'RSRoute')",
  "app_url": "Application URL for OpenRouter rankings (default: 'https://www.rsroute.freedev.app/')",
  "app_categories": "List of category strings for OpenRouter rankings",
  "providers": "OpenRouter provider preferences dictionary (e.g. {'order': ['OpenAI']})"
}
```

### 5.5 OpenAI: `GET /v1/openai/parameters`
```json
{
  "query": "Input to Model",
  "master_key": "rsroute key, mandatory to send response, change it in `.env`",
  "model": "Model name, default is gpt-6-luna",
  "temperature": "Creativity/randomness control (0.0 to 2.0), default is 0.7",
  "max_tokens": "Maximum tokens to generate in each request, default is 4096",
  "max_retries": "Maximum automated retry attempts on request failure, default is 2",
  "timeout": "Network request timeout in seconds, default is 60",
  "use_response_api": "Whether to use the OpenAI Responses API instead of Chat Completions (default: False)",
  "organization_id": "OpenAI organization identifier, default picked from .env",
  "end_point": "Custom url to connect to model.",
  "tools_info": "Bind Your Tool. (only in `/agent` mode)",
  "tools_info_example (not a parameter)": "[{\"name\": \"tool_name\", \"description\": \"tool_description\"}, {\"name\": \"tool2_name\", \"description\": \"description of tool2\"}]"
}
```

---

## 6. Return Formats & Schemas

The server uses Pydantic models to guarantee consistent JSON response schemas across all endpoints.

### 6.1 Chat Response Schema: `ResponseTemplate` (or `ChatTemplate`)

Used by `/v1/gemini/chat`, `/v1/mistral/chat`, `/v1/groq/chat`, `/v1/openrouter/chat`, and `/v1/openai/chat`.

```json
{
  "content": "string | list | any",
  "query": "any",
  "error": "string",
  "login": "boolean",
  "auth": "boolean",
  "usage_metadata": {
    "input_tokens": 12,
    "output_tokens": 45,
    "total_tokens": 57
  },
  "response_metadata": {
    "finish_reason": "stop",
    "model_name": "..."
  },
  "initlized_parameters": {
    "model": "...",
    "temperature": 0.7,
    "max_tokens": 4096,
    "end_point": null
  }
}
```

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `content` | `Any` | Generated message content from the LLM. Contains error summary on failure. |
| `query` | `Any` | Echo of the query provided in the request. |
| `error` | `string` | `"No Error Found"` on success; descriptive error message on failure. |
| `login` | `boolean` | `true` if `master_key` authenticated successfully; `false` on auth failure. |
| `auth` | `boolean` | `true` if server has authentication enabled (`ENABLE_AUTH=true`), otherwise `false`. |
| `usage_metadata` | `object` \| `null` | Token consumption breakdown (input, output, total). `null` if model call did not complete. |
| `response_metadata` | `object` \| `null` | Provider-specific completion details. `null` if model call did not complete. |
| `initlized_parameters` | `object` \| `null` | Dictionary of parameters passed during model initialization via `get_params()`. `null` on early failure. |

---

### 6.2 Agent Response Schema: `AgentTemplate`

Used by `/v1/gemini/agent`, `/v1/mistral/agent`, `/v1/groq/agent`, `/v1/openrouter/agent`, and `/v1/openai/agent`.

Contains all fields from `ResponseTemplate`, with the addition of `tool_calls`:

```json
{
  "content": "string | list | any",
  "tool_calls": [
    {
      "name": "string",
      "args": { "param1": "value1" },
      "id": "string",
      "type": "tool_call"
    }
  ],
  "query": "any",
  "error": "string",
  "login": "boolean",
  "auth": "boolean",
  "usage_metadata": {
    "input_tokens": 30,
    "output_tokens": 20,
    "total_tokens": 50
  },
  "response_metadata": {
    "finish_reason": "tool_calls"
  },
  "initlized_parameters": {
    "model": "...",
    "temperature": 0.7,
    "max_tokens": 4096,
    "binded_tools": [
      {
        "name": "web_search",
        "description": "..."
      }
    ]
  }
}
```

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `tool_calls` | `List[Dict[str, Any]]` | List of tool calls requested by the model. Each item contains `name` (tool identifier), `args` (dictionary of extracted arguments), `id` (call ID), and `type`. Empty list `[]` if the agent answers directly without requesting tools or if request failed early. |
| `initlized_parameters.binded_tools` | `List[Dict[str, str]]` | Confirms the tools successfully bound to the model during initialization. |

---

## 7. Concrete Return Examples

### 7.1 Successful Agent Response (Tool Call Generated)
```json
{
  "content": "",
  "tool_calls": [
    {
      "name": "web_search",
      "args": {
        "query": "Python latest stable release 2026"
      },
      "id": "call_9812491a82bc",
      "type": "tool_call"
    }
  ],
  "query": ["What is the latest release of Python?"],
  "error": "No Error Found",
  "login": true,
  "auth": true,
  "usage_metadata": {
    "input_tokens": 42,
    "output_tokens": 18,
    "total_tokens": 60
  },
  "response_metadata": {
    "finish_reason": "tool_calls"
  },
  "initlized_parameters": {
    "model": "gemini-3.5-flash-lite",
    "temperature": 0.7,
    "max_tokens": 4096,
    "top_p": 1.0,
    "end_point": null,
    "thinking_level": null,
    "thinking_budget": null,
    "binded_tools": [
      {
        "name": "web_search",
        "description": "Performs web searches using DuckDuckGo/DDGS"
      }
    ]
  }
}
```

### 7.2 Authentication Failure (Invalid or Missing `master_key`)
```json
{
  "content": "Authentication Failed",
  "tool_calls": [],
  "query": ["Hello"],
  "error": "given master_key should start with `RSRoute_`.",
  "login": false,
  "auth": true,
  "usage_metadata": null,
  "response_metadata": null,
  "initlized_parameters": null
}
```

### 7.3 Missing Provider API Key
```json
{
  "content": "Invalid Request",
  "tool_calls": [],
  "query": ["Hello"],
  "error": "No OpenAI API Key Found, try to edit `.env`",
  "login": true,
  "auth": true,
  "usage_metadata": null,
  "response_metadata": null,
  "initlized_parameters": null
}
```

### 7.4 Missing OpenAI Organization ID
```json
{
  "content": "Invalid Request",
  "tool_calls": [],
  "query": ["Hello"],
  "error": "No OpenAI Organization ID Found, try to edit `.env`",
  "login": true,
  "auth": true,
  "usage_metadata": null,
  "response_metadata": null,
  "initlized_parameters": null
}
```

### 7.5 Invalid Tool Specification
```json
{
  "content": "Invalid Request",
  "tool_calls": [],
  "query": ["Hello"],
  "error": "Tools must follow the order. [{'name' : 'name of tool', 'description': 'description of tool'}]",
  "login": true,
  "auth": true,
  "usage_metadata": null,
  "response_metadata": null,
  "initlized_parameters": null
}
```

---

## 8. Provider Python API Reference (`app/providers`)

For programmatic usage inside Python without HTTP requests:

```python
from app.providers import (
    BaseChatModel,
    BaseAgentModel,
    ChatGemini,
    GeminiAgent,
    ChatMistralAI,
    MistralAgent,
    ChatGroq,
    GroqAgent,
    ChatOpenRouter,
    OpenRouterAgent,
    ChatOpenAI,
    OpenAIAgent
)

# Standard Chat Model instantiation (OpenAI)
chat_model = ChatOpenAI(
    api_key="your_api_key",
    model="gpt-6-luna",
    temperature=0.7,
    max_tokens=4096,
    timeout=60,
    organization_id="your_org_id"
)
response = chat_model("Hello!")  # Or chat_model.generate("Hello!")
params = chat_model.get_params()

# Agent Model instantiation with tools (OpenAI)
agent = OpenAIAgent(
    api_key="your_api_key",
    model="gpt-6-luna",
    organization_id="your_org_id",
    tools_info=[{"name": "web_search", "description": "Search the web"}]
)
agent_response = agent("What is the latest news?")
# agent_response is a LangChain AIMessage with .tool_calls and .content
```
