ROOT_URL = "http://0.0.0.0:8000/"
GEMINI_URL = "http://0.0.0.0:8000/v1/gemini/chat"
MISTRAL_URL = "http://0.0.0.0:8000/v1/mistral/chat"


# Agentic Routes
GEMINI_AGENT = "http://0.0.0.0:8000/v1/gemini/agent"


URLS = {
    "root": ROOT_URL,
    "gemini": GEMINI_URL,
    "mistral": MISTRAL_URL,
    "gemini_agent": GEMINI_AGENT
}


END_POINTS = {
    "root": "/",
    "gemini": "/v1/gemini/chat",
    "mistral": "/v1/mistral/chat",
    "gemini_agent": "/v1/gemini/agent"
}

