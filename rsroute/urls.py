ROOT_URL = "http://0.0.0.0:8000/"
GEMINI = f"{ROOT_URL}v1/gemini"
MISTRAL = f"{ROOT_URL}v1/mistral"
OPENROUTER = f"{ROOT_URL}v1/openrouter"
OPENAI = f"{ROOT_URL}v1/openai"
GROQ = f"{ROOT_URL}v1/groq"


GEMINI_URL = f"{GEMINI}/chat"
MISTRAL_URL = f"{MISTRAL}/chat"
GROQ_URL = f"{GROQ}/chat"
OPENROUTER_URL = f"{OPENROUTER}/chat"
OPENAI_URL = f"{OPENAI}/chat"


# Agentic Routes
GEMINI_AGENT = f"{GEMINI}/agent"
MISTRAL_AGENT = f"{MISTRAL}/agent"
GROQ_AGENT = f"{GROQ}/agent"
OPENROUTER_AGENT = f"{OPENROUTER}/agent"
OPENAI_AGENT = f"{OPENAI}/agent"


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


PARAMS_URL = {
    "gemini": f"{GEMINI}/parameters",
    "groq": f"{GROQ}/parameters",
    "openrouter": f"{OPENROUTER}/parameters",
    "openai": f"{OPENAI}/parameters",
    "mistral": f"{MISTRAL}/parameters"
}