ROOT_URL = "http://0.0.0.0:8000/"
GEMINI_URL = "http://0.0.0.0:8000/v1/gemini/chat"
MISTRAL_URL = "http://0.0.0.0:8000/v1/mistral/chat"
GROQ_URL = "http://0.0.0.0:8000/v1/groq/chat"


# Agentic Routes
GEMINI_AGENT = "http://0.0.0.0:8000/v1/gemini/agent"
MISTRAL_AGENT = "http://0.0.0.0:8000/v1/mistral/agent"
GROQ_AGENT = "http://0.0.0.0:8000/v1/groq/agent"


URLS = {
    "root": ROOT_URL,
    "gemini": GEMINI_URL,
    "mistral": MISTRAL_URL,
    "groq": GROQ_URL,
    "gemini_agent": GEMINI_AGENT,
    "mistral_agent": MISTRAL_AGENT,
    "groq_agent": GROQ_AGENT,
}


END_POINTS = {
    "root": "/",
    "gemini": "/v1/gemini/chat",
    "mistral": "/v1/mistral/chat",
    "groq": "/v1/groq/chat",
    "gemini_agent": "/v1/gemini/agent",
    "mistral_agent": "/v1/mistral/agent",
    "groq_agent": "/v1/groq/agent",
}
