ROOT_URL = "http://0.0.0.0:8000/"
GEMINI_URL = "http://0.0.0.0:8000/v1/gemini/chat"
MISTRAL_URL = "http://0.0.0.0:8000/v1/mistral/chat"
GROQ_URL = "http://0.0.0.0:8000/v1/groq/chat"
OPENROUTER_URL = "http://0.0.0.0:8000/v1/openrouter/chat"
OPENAI_URL = "http://0.0.0.0:8000/v1/openai/chat"


# Agentic Routes
GEMINI_AGENT = "http://0.0.0.0:8000/v1/gemini/agent"
MISTRAL_AGENT = "http://0.0.0.0:8000/v1/mistral/agent"
GROQ_AGENT = "http://0.0.0.0:8000/v1/groq/agent"
OPENROUTER_AGENT = "http://0.0.0.0:8000/v1/openrouter/agent"
OPENAI_AGENT = "http://0.0.0.0:8000/v1/openai/agent"


URLS = {
    "root": ROOT_URL,
    "gemini": GEMINI_URL,
    "mistral": MISTRAL_URL,
    "groq": GROQ_URL,
    "openrouter": OPENROUTER_URL,
    "gemini_agent": GEMINI_AGENT,
    "mistral_agent": MISTRAL_AGENT,
    "groq_agent": GROQ_AGENT,
    "openrouter_agent": OPENROUTER_AGENT,
    "openai": OPENAI_URL,
    "openai_agent": OPENAI_AGENT
}


END_POINTS = {
    "root": "/",
    "gemini": "/v1/gemini/chat",
    "mistral": "/v1/mistral/chat",
    "groq": "/v1/groq/chat",
    "openrouter": "/v1/openrouter/chat",
    "gemini_agent": "/v1/gemini/agent",
    "mistral_agent": "/v1/mistral/agent",
    "groq_agent": "/v1/groq/agent",
    "openrouter_agent": "/v1/openrouter/agent",
    "openai": "/v1/openai/chat",
    "openai_agent": "/v1/openai/agent"
}
