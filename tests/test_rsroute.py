import unittest
from unittest.mock import patch, MagicMock
from langchain_core.tools import tool, StructuredTool

from rsroute.urls import URLS, END_POINTS
from rsroute.chat_models import (
    ChatGemini,
    ChatMistral,
    ChatMistralAI,
    MistralAI,
    ChatGroq,
    ChatOpenRouter,
    OpenRouter,
    ChatGPT,
    ChatOpenAI,
)
from rsroute.agents import (
    GeminiAgent,
    MistralAgent,
    GroqAgent,
    OpenRouterAgent,
    ChatOpenRouterAgent,
    GPTAgent,
    OpenAIAgent,
    ChatGPTAgent,
)
from rsroute.base import BaseEstimator, BaseEstimatorAgent


@tool
def add_numbers(a: int, b: int) -> int:
    """Adds two integers."""
    return a + b


@tool
def echo_text(text: str) -> str:
    """Echoes input text."""
    return text


class TestUrls(unittest.TestCase):
    def test_urls_and_endpoints(self):
        self.assertEqual(URLS["groq"], "http://0.0.0.0:8000/v1/groq/chat")
        self.assertEqual(URLS["mistral_agent"], "http://0.0.0.0:8000/v1/mistral/agent")
        self.assertEqual(URLS["groq_agent"], "http://0.0.0.0:8000/v1/groq/agent")
        self.assertEqual(URLS["openrouter"], "http://0.0.0.0:8000/v1/openrouter/chat")
        self.assertEqual(URLS["openrouter_agent"], "http://0.0.0.0:8000/v1/openrouter/agent")
        self.assertEqual(URLS["openrouter_parameters"], "http://0.0.0.0:8000/v1/openrouter/parameters")
        self.assertEqual(URLS["openrouter_parameter"], "http://0.0.0.0:8000/v1/openrouter/parameter")

        self.assertEqual(END_POINTS["groq"], "/v1/groq/chat")
        self.assertEqual(END_POINTS["mistral_agent"], "/v1/mistral/agent")
        self.assertEqual(END_POINTS["groq_agent"], "/v1/groq/agent")
        self.assertEqual(END_POINTS["openrouter"], "/v1/openrouter/chat")
        self.assertEqual(END_POINTS["openrouter_agent"], "/v1/openrouter/agent")
        self.assertEqual(END_POINTS["openrouter_parameters"], "/v1/openrouter/parameters")
        self.assertEqual(END_POINTS["openrouter_parameter"], "/v1/openrouter/parameter")

    def test_openai_urls_and_endpoints(self):
        self.assertEqual(URLS["openai"], "http://0.0.0.0:8000/v1/openai/chat")
        self.assertEqual(URLS["openai_agent"], "http://0.0.0.0:8000/v1/openai/agent")
        self.assertEqual(END_POINTS["openai"], "/v1/openai/chat")
        self.assertEqual(END_POINTS["openai_agent"], "/v1/openai/agent")


class TestChatGroq(unittest.TestCase):
    def test_default_initialization(self):
        client = ChatGroq(master_key="RSRoute_test_key")
        self.assertEqual(client.rsroute_url, "http://0.0.0.0:8000/v1/groq/chat")
        self.assertEqual(client.request_data["master_key"], "RSRoute_test_key")
        self.assertNotIn("model", client.request_data)
        self.assertNotIn("top_p", client.request_data)

    def test_custom_parameters(self):
        client = ChatGroq(
            master_key="RSRoute_test_key",
            model="openai/gpt-oss-120b",
            temperature=0.7,
            max_tokens=1024,
            end_point="http://custom-proxy/v1",
            timeout=45,
            rsroute_url="http://custom-server:9000",
        )
        self.assertEqual(client.rsroute_url, "http://custom-server:9000/v1/groq/chat")
        self.assertEqual(client.timeout, 45)
        self.assertEqual(client.request_data["model"], "openai/gpt-oss-120b")
        self.assertEqual(client.request_data["temperature"], 0.7)
        self.assertEqual(client.request_data["max_tokens"], 1024)
        self.assertEqual(client.request_data["end_point"], "http://custom-proxy/v1")
        self.assertNotIn("top_p", client.request_data)
        self.assertNotIn("thinking_level", client.request_data)
        self.assertNotIn("thinking_budget", client.request_data)

    def test_get_params(self):
        client = ChatGroq(
            master_key="RSRoute_test_key",
            model="openai/gpt-oss-120b",
            temperature=0.5,
        )
        params = client.get_params()
        self.assertNotIn("master_key", params)
        self.assertNotIn("top_p", params)
        self.assertEqual(params["model"], "openai/gpt-oss-120b")
        self.assertEqual(params["temperature"], 0.5)

    @patch("requests.post")
    def test_invoke_string_query(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": "Hello from Groq!",
            "query": [{"role": "user", "content": "Hi"}],
            "error": "No Error Found",
            "login": True,
            "auth": True,
        }
        mock_post.return_value = mock_response

        client = ChatGroq(master_key="RSRoute_test_key")
        result = client.invoke("Hi")

        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        self.assertEqual(
            kwargs["json"]["query"],
            [{"role": "user", "content": "Hi"}]
        )
        self.assertEqual(result["content"], "Hello from Groq!")

    @patch("requests.post")
    def test_call_and_generate(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": "ok"}
        mock_post.return_value = mock_response

        client = ChatGroq(master_key="RSRoute_test_key")
        res1 = client("test 1")
        res2 = client.generate("test 2")
        self.assertEqual(res1["content"], "ok")
        self.assertEqual(res2["content"], "ok")
        self.assertEqual(mock_post.call_count, 2)


class TestMistralAgent(unittest.TestCase):
    def test_initialization(self):
        agent = MistralAgent(
            tools=[add_numbers],
            master_key="RSRoute_test_key",
            model="mistral-small-2603",
            temperature=0.2,
            max_tokens=2048,
        )
        self.assertEqual(agent.rsroute_url, "http://0.0.0.0:8000/v1/mistral/agent")
        self.assertEqual(agent.request_data["model"], "mistral-small-2603")
        self.assertEqual(agent.request_data["temperature"], 0.2)
        self.assertEqual(agent.request_data["max_tokens"], 2048)
        self.assertEqual(
            agent.tools_info,
            [{"name": "add_numbers", "description": "Adds two integers."}]
        )
        self.assertNotIn("top_p", agent.request_data)
        self.assertNotIn("thinking_level", agent.request_data)
        self.assertNotIn("thinking_budget", agent.request_data)
        self.assertNotIn("kwargs", agent.request_data)

    def test_custom_rsroute_url(self):
        agent = MistralAgent(
            tools=[add_numbers],
            master_key="RSRoute_test_key",
            rsroute_url="http://my-host:8080/",
        )
        self.assertEqual(agent.rsroute_url, "http://my-host:8080/v1/mistral/agent")

    def test_empty_tools_raises_error(self):
        with self.assertRaises(ValueError):
            MistralAgent(tools=[], master_key="RSRoute_test_key")

    def test_invalid_tool_type_raises_error(self):
        with self.assertRaises(TypeError):
            MistralAgent(tools=["not_a_tool"], master_key="RSRoute_test_key")

    @patch("requests.post")
    def test_agent_tool_loop(self, mock_post):
        mock_response_1 = MagicMock()
        mock_response_1.json.return_value = {
            "content": "",
            "tool_calls": [
                {
                    "name": "add_numbers",
                    "args": {"a": 5, "b": 7},
                    "id": "call_123",
                    "type": "tool_call",
                }
            ],
            "query": ["What is 5 + 7?"],
            "error": "No Error Found",
        }

        mock_response_2 = MagicMock()
        mock_response_2.json.return_value = {
            "content": "The sum is 12.",
            "tool_calls": [],
            "query": ["What is 5 + 7?"],
            "error": "No Error Found",
        }

        mock_post.side_effect = [mock_response_1, mock_response_2]

        agent = MistralAgent(
            tools=[add_numbers],
            master_key="RSRoute_test_key",
        )
        result = agent.invoke("What is 5 + 7?")
        self.assertEqual(result["content"], "The sum is 12.")
        self.assertEqual(mock_post.call_count, 2)


class TestGroqAgent(unittest.TestCase):
    def test_initialization(self):
        agent = GroqAgent(
            tools=[echo_text],
            master_key="RSRoute_test_key",
            model="openai/gpt-oss-120b",
            temperature=0.7,
            max_tokens=4096,
        )
        self.assertEqual(agent.rsroute_url, "http://0.0.0.0:8000/v1/groq/agent")
        self.assertEqual(agent.request_data["model"], "openai/gpt-oss-120b")
        self.assertEqual(agent.request_data["temperature"], 0.7)
        self.assertEqual(agent.request_data["max_tokens"], 4096)
        self.assertEqual(
            agent.tools_info,
            [{"name": "echo_text", "description": "Echoes input text."}]
        )
        self.assertNotIn("top_p", agent.request_data)
        self.assertNotIn("thinking_level", agent.request_data)
        self.assertNotIn("thinking_budget", agent.request_data)
        self.assertNotIn("kwargs", agent.request_data)

    def test_custom_rsroute_url(self):
        agent = GroqAgent(
            tools=[echo_text],
            master_key="RSRoute_test_key",
            rsroute_url="http://my-host:8080/",
        )
        self.assertEqual(agent.rsroute_url, "http://my-host:8080/v1/groq/agent")

    @patch("requests.post")
    def test_ainvoke_direct_call(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": "Direct response without tool loop",
            "tool_calls": [{"name": "echo_text", "args": {"text": "hi"}, "id": "1", "type": "tool_call"}],
        }
        mock_post.return_value = mock_response

        agent = GroqAgent(
            tools=[echo_text],
            master_key="RSRoute_test_key",
        )
        result = agent.ainvoke("hi")
        self.assertEqual(result["content"], "Direct response without tool loop")
        self.assertEqual(len(result["tool_calls"]), 1)
        self.assertEqual(mock_post.call_count, 1)

    @patch("requests.post")
    def test_tool_loop_execution(self, mock_post):
        resp1 = MagicMock()
        resp1.json.return_value = {
            "content": "",
            "tool_calls": [{"name": "echo_text", "args": {"text": "hello groq"}, "id": "call_1", "type": "tool_call"}],
        }
        resp2 = MagicMock()
        resp2.json.return_value = {
            "content": "echoed: hello groq",
            "tool_calls": [],
        }
        mock_post.side_effect = [resp1, resp2]

        agent = GroqAgent(
            tools=[echo_text],
            master_key="RSRoute_test_key",
        )
        result = agent.invoke("Say hello")
        self.assertEqual(result["content"], "echoed: hello groq")
        self.assertEqual(mock_post.call_count, 2)


class TestChatMistralAliases(unittest.TestCase):
    def test_aliases(self):
        self.assertIs(ChatMistralAI, ChatMistral)
        self.assertIs(MistralAI, ChatMistral)

        client = ChatMistralAI(master_key="RSRoute_test_key", temperature=0.3)
        self.assertEqual(client.request_data["temperature"], 0.3)
        self.assertNotIn("top_p", client.request_data)


class TestGeminiAgent(unittest.TestCase):
    def test_initialization(self):
        agent = GeminiAgent(
            tools=[add_numbers],
            master_key="RSRoute_test_key",
            model="gemini-3.5-flash-lite",
            temperature=0.5,
            thinking_level="high",
            thinking_budget=1024,
        )
        self.assertEqual(agent.rsroute_url, "http://0.0.0.0:8000/v1/gemini/agent")
        self.assertEqual(agent.request_data["model"], "gemini-3.5-flash-lite")
        self.assertEqual(agent.request_data["temperature"], 0.5)
        self.assertEqual(agent.request_data["thinking_level"], "high")
        self.assertEqual(agent.request_data["thinking_budget"], 1024)

    @patch("requests.post")
    def test_invoke_unwraps_single_list_content(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": [{"text": "Extracted answer", "extras": {"thought": "deep"}}],
            "tool_calls": [],
        }
        mock_post.return_value = mock_response

        agent = GeminiAgent(tools=[add_numbers], master_key="RSRoute_test_key")
        result = agent.invoke("What is life?")
        self.assertEqual(result["content"], "Extracted answer")
        self.assertEqual(result["extras"], {"thought": "deep"})

    @patch("requests.post")
    def test_invoke_preserves_multiple_list_content(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": [{"text": "Item 1"}, {"text": "Item 2"}],
            "tool_calls": [],
        }
        mock_post.return_value = mock_response

        agent = GeminiAgent(tools=[add_numbers], master_key="RSRoute_test_key")
        result = agent.invoke("Tell me items")
        self.assertEqual(len(result["content"]), 2)

    @patch("requests.post")
    def test_invoke_preserves_string_content(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": "Regular text response",
            "tool_calls": [],
        }
        mock_post.return_value = mock_response

        agent = GeminiAgent(tools=[add_numbers], master_key="RSRoute_test_key")
        result = agent.invoke("Hello")
        self.assertEqual(result["content"], "Regular text response")


class TestUsageMetadataAccumulation(unittest.TestCase):
    @patch("requests.post")
    def test_token_accumulation_in_tool_loop(self, mock_post):
        resp1 = MagicMock()
        resp1.json.return_value = {
            "content": "",
            "tool_calls": [{"name": "add_numbers", "args": {"a": 2, "b": 3}, "id": "call_1", "type": "tool_call"}],
            "usage_metadata": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
        }
        resp2 = MagicMock()
        resp2.json.return_value = {
            "content": "Result is 5",
            "tool_calls": [],
            "usage_metadata": {"input_tokens": 20, "output_tokens": 8, "total_tokens": 28},
        }
        mock_post.side_effect = [resp1, resp2]

        agent = MistralAgent(tools=[add_numbers], master_key="RSRoute_test_key")
        result = agent.invoke("2 + 3")
        self.assertEqual(result["usage_metadata"]["input_tokens"], 30)
        self.assertEqual(result["usage_metadata"]["output_tokens"], 13)
        self.assertEqual(result["usage_metadata"]["total_tokens"], 43)


class TestTopPRemovedAcrossAllModels(unittest.TestCase):
    def test_chat_gemini_no_top_p(self):
        client = ChatGemini(master_key="RSRoute_test_key", temperature=0.7)
        self.assertNotIn("top_p", client.request_data)

    def test_gemini_agent_no_top_p(self):
        agent = GeminiAgent(tools=[add_numbers], master_key="RSRoute_test_key")
        self.assertNotIn("top_p", agent.request_data)

    def test_chat_mistral_no_top_p(self):
        client = ChatMistral(master_key="RSRoute_test_key", temperature=0.7)
        self.assertNotIn("top_p", client.request_data)

    def test_mistral_agent_no_top_p(self):
        agent = MistralAgent(tools=[add_numbers], master_key="RSRoute_test_key")
        self.assertNotIn("top_p", agent.request_data)

    def test_chat_groq_no_top_p(self):
        client = ChatGroq(master_key="RSRoute_test_key", temperature=0.7)
        self.assertNotIn("top_p", client.request_data)

    def test_groq_agent_no_top_p(self):
        agent = GroqAgent(tools=[add_numbers], master_key="RSRoute_test_key")
        self.assertNotIn("top_p", agent.request_data)

    def test_chat_openrouter_no_top_p(self):
        client = ChatOpenRouter(master_key="RSRoute_test_key", temperature=0.7)
        self.assertNotIn("top_p", client.request_data)

    def test_openrouter_agent_no_top_p(self):
        agent = OpenRouterAgent(tools=[add_numbers], master_key="RSRoute_test_key")
        self.assertNotIn("top_p", agent.request_data)


class TestChatOpenRouter(unittest.TestCase):
    def test_default_initialization(self):
        client = ChatOpenRouter(master_key="RSRoute_test_key")
        self.assertEqual(client.rsroute_url, "http://0.0.0.0:8000/v1/openrouter/chat")
        self.assertEqual(client.request_data["master_key"], "RSRoute_test_key")
        self.assertNotIn("model", client.request_data)
        self.assertNotIn("top_p", client.request_data)
        self.assertNotIn("thinking_level", client.request_data)
        self.assertNotIn("thinking_budget", client.request_data)

    def test_custom_parameters(self):
        client = ChatOpenRouter(
            master_key="RSRoute_test_key",
            model="deepseek/deepseek-v4.1-flash",
            temperature=0.7,
            max_tokens=4096,
            app_title="RSRoute",
            app_url="https://www.rsroute.freedev.app/",
            app_categories=["ai", "developer-tools"],
            max_retries=2,
            providers={"order": ["OpenAI"]},
            end_point="http://custom-proxy/v1",
            timeout=45,
            rsroute_url="http://custom-server:9000",
        )
        self.assertEqual(client.rsroute_url, "http://custom-server:9000/v1/openrouter/chat")
        self.assertEqual(client.timeout, 45)
        self.assertEqual(client.request_data["model"], "deepseek/deepseek-v4.1-flash")
        self.assertEqual(client.request_data["temperature"], 0.7)
        self.assertEqual(client.request_data["max_tokens"], 4096)
        self.assertEqual(client.request_data["app_title"], "RSRoute")
        self.assertEqual(client.request_data["app_url"], "https://www.rsroute.freedev.app/")
        self.assertEqual(client.request_data["app_categories"], ["ai", "developer-tools"])
        self.assertEqual(client.request_data["max_retries"], 2)
        self.assertEqual(client.request_data["providers"], {"order": ["OpenAI"]})
        self.assertEqual(client.request_data["end_point"], "http://custom-proxy/v1")
        self.assertNotIn("top_p", client.request_data)
        self.assertNotIn("thinking_level", client.request_data)
        self.assertNotIn("thinking_budget", client.request_data)

    def test_get_params(self):
        client = ChatOpenRouter(
            master_key="RSRoute_test_key",
            model="deepseek/deepseek-v4.1-flash",
            temperature=0.7,
            app_title="RSRoute",
        )
        params = client.get_params()
        self.assertNotIn("master_key", params)
        self.assertNotIn("top_p", params)
        self.assertEqual(params["model"], "deepseek/deepseek-v4.1-flash")
        self.assertEqual(params["temperature"], 0.7)
        self.assertEqual(params["app_title"], "RSRoute")

    @patch("requests.post")
    def test_invoke_string_query(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": "Hello from OpenRouter!",
            "query": [{"role": "user", "content": "Hi"}],
            "error": "No Error Found",
            "login": True,
            "auth": True,
        }
        mock_post.return_value = mock_response

        client = ChatOpenRouter(master_key="RSRoute_test_key")
        result = client.invoke("Hi")

        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        self.assertEqual(
            kwargs["json"]["query"],
            [{"role": "user", "content": "Hi"}]
        )
        self.assertEqual(result["content"], "Hello from OpenRouter!")

    @patch("requests.post")
    def test_call_and_generate(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": "ok"}
        mock_post.return_value = mock_response

        client = ChatOpenRouter(master_key="RSRoute_test_key")
        res1 = client("test 1")
        res2 = client.generate("test 2")
        self.assertEqual(res1["content"], "ok")
        self.assertEqual(res2["content"], "ok")
        self.assertEqual(mock_post.call_count, 2)

    def test_alias(self):
        self.assertIs(OpenRouter, ChatOpenRouter)


class TestOpenRouterAgent(unittest.TestCase):
    def test_initialization(self):
        agent = OpenRouterAgent(
            tools=[echo_text],
            master_key="RSRoute_test_key",
            model="deepseek/deepseek-v4.1-flash",
            temperature=0.7,
            max_tokens=4096,
            app_title="RSRoute",
            app_url="https://www.rsroute.freedev.app/",
            app_categories=["ai"],
            max_retries=2,
            providers={"order": ["OpenAI"]},
        )
        self.assertEqual(agent.rsroute_url, "http://0.0.0.0:8000/v1/openrouter/agent")
        self.assertEqual(agent.request_data["model"], "deepseek/deepseek-v4.1-flash")
        self.assertEqual(agent.request_data["temperature"], 0.7)
        self.assertEqual(agent.request_data["max_tokens"], 4096)
        self.assertEqual(agent.request_data["app_title"], "RSRoute")
        self.assertEqual(agent.request_data["app_url"], "https://www.rsroute.freedev.app/")
        self.assertEqual(agent.request_data["app_categories"], ["ai"])
        self.assertEqual(agent.request_data["max_retries"], 2)
        self.assertEqual(agent.request_data["providers"], {"order": ["OpenAI"]})
        self.assertEqual(
            agent.tools_info,
            [{"name": "echo_text", "description": "Echoes input text."}]
        )
        self.assertNotIn("top_p", agent.request_data)
        self.assertNotIn("thinking_level", agent.request_data)
        self.assertNotIn("thinking_budget", agent.request_data)

    def test_custom_rsroute_url(self):
        agent = OpenRouterAgent(
            tools=[echo_text],
            master_key="RSRoute_test_key",
            rsroute_url="http://my-host:8080/",
        )
        self.assertEqual(agent.rsroute_url, "http://my-host:8080/v1/openrouter/agent")

    @patch("requests.post")
    def test_ainvoke_direct_call(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": "Direct response without tool loop",
            "tool_calls": [{"name": "echo_text", "args": {"text": "hi"}, "id": "1", "type": "tool_call"}],
        }
        mock_post.return_value = mock_response

        agent = OpenRouterAgent(
            tools=[echo_text],
            master_key="RSRoute_test_key",
        )
        result = agent.ainvoke("hi")
        self.assertEqual(result["content"], "Direct response without tool loop")
        self.assertEqual(len(result["tool_calls"]), 1)
        self.assertEqual(mock_post.call_count, 1)

    @patch("requests.post")
    def test_tool_loop_execution(self, mock_post):
        resp1 = MagicMock()
        resp1.json.return_value = {
            "content": "",
            "tool_calls": [{"name": "echo_text", "args": {"text": "hello openrouter"}, "id": "call_1", "type": "tool_call"}],
        }
        resp2 = MagicMock()
        resp2.json.return_value = {
            "content": "echoed: hello openrouter",
            "tool_calls": [],
        }
        mock_post.side_effect = [resp1, resp2]

        agent = OpenRouterAgent(
            tools=[echo_text],
            master_key="RSRoute_test_key",
        )
        result = agent.invoke("Say hello")
        self.assertEqual(result["content"], "echoed: hello openrouter")
        self.assertEqual(mock_post.call_count, 2)

    @patch("requests.post")
    def test_invoke_unwraps_single_list_content(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": [{"text": "Extracted answer", "extras": {"thought": "deep"}}],
            "tool_calls": [],
        }
        mock_post.return_value = mock_response

        agent = OpenRouterAgent(tools=[add_numbers], master_key="RSRoute_test_key")
        result = agent.invoke("What is life?")
        self.assertEqual(result["content"], "Extracted answer")
        self.assertEqual(result["extras"], {"thought": "deep"})

    @patch("requests.post")
    def test_invoke_preserves_string_content(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": "Regular text response",
            "tool_calls": [],
        }
        mock_post.return_value = mock_response

        agent = OpenRouterAgent(tools=[add_numbers], master_key="RSRoute_test_key")
        result = agent.invoke("Hello")
        self.assertEqual(result["content"], "Regular text response")

    def test_alias(self):
        self.assertIs(ChatOpenRouterAgent, OpenRouterAgent)


# ---------------------------------------------------------------------------
# ChatGPT / ChatOpenAI Tests
# ---------------------------------------------------------------------------

class TestChatGPT(unittest.TestCase):
    @patch("rsroute.chat_models.openai_client.get_org_id", return_value="org-test123")
    def test_default_initialization(self, mock_org):
        client = ChatGPT(master_key="RSRoute_test_key")
        self.assertEqual(client.rsroute_url, "http://0.0.0.0:8000/v1/openai/chat")
        self.assertEqual(client.request_data["master_key"], "RSRoute_test_key")
        self.assertEqual(client.request_data["organization_id"], "org-test123")
        self.assertNotIn("model", client.request_data)
        self.assertNotIn("top_p", client.request_data)
        self.assertNotIn("thinking_level", client.request_data)

    @patch("rsroute.chat_models.openai_client.get_org_id", return_value=None)
    def test_explicit_organization_id(self, mock_org):
        client = ChatGPT(
            master_key="RSRoute_test_key",
            organization_id="org-explicit",
        )
        self.assertEqual(client.request_data["organization_id"], "org-explicit")

    @patch("rsroute.chat_models.openai_client.get_org_id", return_value=None)
    def test_org_id_alias(self, mock_org):
        client = ChatGPT(
            master_key="RSRoute_test_key",
            org_id="org-via-alias",
        )
        self.assertEqual(client.request_data["organization_id"], "org-via-alias")

    @patch("rsroute.chat_models.openai_client.get_org_id", return_value=None)
    def test_no_org_id_stores_none(self, mock_org):
        """When org id is None everywhere, organization_id should not be in request_data."""
        client = ChatGPT(master_key="RSRoute_test_key")
        # None values are excluded by BaseEstimator's kwargs loop
        self.assertNotIn("organization_id", client.request_data)

    @patch("rsroute.chat_models.openai_client.get_org_id", return_value="org-env")
    def test_custom_parameters(self, mock_org):
        client = ChatGPT(
            master_key="RSRoute_test_key",
            model="gpt-6-luna",
            temperature=0.5,
            max_tokens=2048,
            timeout=90,
            end_point="http://custom-proxy/v1",
            max_retries=3,
            use_response_api=True,
            rsroute_url="http://custom-server:9000",
        )
        self.assertEqual(client.rsroute_url, "http://custom-server:9000/v1/openai/chat")
        self.assertEqual(client.timeout, 90)
        self.assertEqual(client.request_data["model"], "gpt-6-luna")
        self.assertEqual(client.request_data["temperature"], 0.5)
        self.assertEqual(client.request_data["max_tokens"], 2048)
        self.assertEqual(client.request_data["end_point"], "http://custom-proxy/v1")
        self.assertEqual(client.request_data["max_retries"], 3)
        self.assertEqual(client.request_data["use_response_api"], True)
        self.assertEqual(client.request_data["organization_id"], "org-env")
        self.assertNotIn("top_p", client.request_data)
        self.assertNotIn("thinking_level", client.request_data)
        self.assertNotIn("thinking_budget", client.request_data)

    @patch("rsroute.chat_models.openai_client.get_org_id", return_value="org-env")
    def test_get_params_excludes_master_key(self, mock_org):
        client = ChatGPT(
            master_key="RSRoute_test_key",
            model="gpt-6-luna",
            temperature=0.7,
        )
        params = client.get_params()
        self.assertNotIn("master_key", params)
        self.assertEqual(params["model"], "gpt-6-luna")
        self.assertEqual(params["temperature"], 0.7)
        self.assertEqual(params["organization_id"], "org-env")

    @patch("rsroute.chat_models.openai_client.get_org_id", return_value="org-env")
    @patch("requests.post")
    def test_invoke_string_query(self, mock_post, mock_org):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": "Hello from OpenAI!",
            "query": [{"role": "user", "content": "Hi"}],
            "error": "No Error Found",
            "login": True,
            "auth": True,
        }
        mock_post.return_value = mock_response

        client = ChatGPT(master_key="RSRoute_test_key")
        result = client.invoke("Hi")

        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        self.assertEqual(
            kwargs["json"]["query"],
            [{"role": "user", "content": "Hi"}]
        )
        self.assertEqual(result["content"], "Hello from OpenAI!")

    @patch("rsroute.chat_models.openai_client.get_org_id", return_value="org-env")
    @patch("requests.post")
    def test_call_and_generate(self, mock_post, mock_org):
        mock_response = MagicMock()
        mock_response.json.return_value = {"content": "ok"}
        mock_post.return_value = mock_response

        client = ChatGPT(master_key="RSRoute_test_key")
        res1 = client("test 1")
        res2 = client.generate("test 2")
        self.assertEqual(res1["content"], "ok")
        self.assertEqual(res2["content"], "ok")
        self.assertEqual(mock_post.call_count, 2)

    def test_aliases(self):
        self.assertIs(ChatOpenAI, ChatGPT)


# ---------------------------------------------------------------------------
# GPTAgent / OpenAIAgent Tests
# ---------------------------------------------------------------------------

class TestGPTAgent(unittest.TestCase):
    @patch("rsroute.agents.openai_agent.get_org_id", return_value="org-test123")
    def test_initialization(self, mock_org):
        agent = GPTAgent(
            tools=[add_numbers],
            master_key="RSRoute_test_key",
            model="gpt-6-luna",
            temperature=0.3,
            max_tokens=4096,
        )
        self.assertEqual(agent.rsroute_url, "http://0.0.0.0:8000/v1/openai/agent")
        self.assertEqual(agent.request_data["model"], "gpt-6-luna")
        self.assertEqual(agent.request_data["temperature"], 0.3)
        self.assertEqual(agent.request_data["max_tokens"], 4096)
        self.assertEqual(agent.request_data["organization_id"], "org-test123")
        self.assertEqual(
            agent.tools_info,
            [{"name": "add_numbers", "description": "Adds two integers."}]
        )
        self.assertNotIn("top_p", agent.request_data)
        self.assertNotIn("thinking_level", agent.request_data)
        self.assertNotIn("thinking_budget", agent.request_data)

    @patch("rsroute.agents.openai_agent.get_org_id", return_value=None)
    def test_explicit_org_id(self, mock_org):
        agent = GPTAgent(
            tools=[echo_text],
            master_key="RSRoute_test_key",
            organization_id="org-explicit",
        )
        self.assertEqual(agent.request_data["organization_id"], "org-explicit")

    @patch("rsroute.agents.openai_agent.get_org_id", return_value=None)
    def test_org_id_alias(self, mock_org):
        agent = GPTAgent(
            tools=[echo_text],
            master_key="RSRoute_test_key",
            org_id="org-alias",
        )
        self.assertEqual(agent.request_data["organization_id"], "org-alias")

    @patch("rsroute.agents.openai_agent.get_org_id", return_value="org-env")
    def test_custom_rsroute_url(self, mock_org):
        agent = GPTAgent(
            tools=[add_numbers],
            master_key="RSRoute_test_key",
            rsroute_url="http://my-host:8080/",
        )
        self.assertEqual(agent.rsroute_url, "http://my-host:8080/v1/openai/agent")

    def test_empty_tools_raises_error(self):
        with self.assertRaises(ValueError):
            GPTAgent(tools=[], master_key="RSRoute_test_key")

    def test_invalid_tool_type_raises_error(self):
        with self.assertRaises(TypeError):
            GPTAgent(tools=["not_a_tool"], master_key="RSRoute_test_key")

    @patch("rsroute.agents.openai_agent.get_org_id", return_value="org-env")
    @patch("requests.post")
    def test_ainvoke_direct_call(self, mock_post, mock_org):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": "Direct response without tool loop",
            "tool_calls": [{"name": "add_numbers", "args": {"a": 1, "b": 2}, "id": "1", "type": "tool_call"}],
        }
        mock_post.return_value = mock_response

        agent = GPTAgent(tools=[add_numbers], master_key="RSRoute_test_key")
        result = agent.ainvoke("hi")
        self.assertEqual(result["content"], "Direct response without tool loop")
        self.assertEqual(len(result["tool_calls"]), 1)
        self.assertEqual(mock_post.call_count, 1)

    @patch("rsroute.agents.openai_agent.get_org_id", return_value="org-env")
    @patch("requests.post")
    def test_agent_tool_loop(self, mock_post, mock_org):
        resp1 = MagicMock()
        resp1.json.return_value = {
            "content": "",
            "tool_calls": [
                {
                    "name": "add_numbers",
                    "args": {"a": 10, "b": 20},
                    "id": "call_abc",
                    "type": "tool_call",
                }
            ],
            "query": ["What is 10 + 20?"],
            "error": "No Error Found",
        }
        resp2 = MagicMock()
        resp2.json.return_value = {
            "content": "The sum is 30.",
            "tool_calls": [],
            "query": ["What is 10 + 20?"],
            "error": "No Error Found",
        }
        mock_post.side_effect = [resp1, resp2]

        agent = GPTAgent(tools=[add_numbers], master_key="RSRoute_test_key")
        result = agent.invoke("What is 10 + 20?")
        self.assertEqual(result["content"], "The sum is 30.")
        self.assertEqual(mock_post.call_count, 2)

    @patch("rsroute.agents.openai_agent.get_org_id", return_value="org-env")
    @patch("requests.post")
    def test_invoke_unwraps_single_list_content(self, mock_post, mock_org):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": [{"text": "OpenAI final answer", "extras": {"detail": "x"}}],
            "tool_calls": [],
        }
        mock_post.return_value = mock_response

        agent = GPTAgent(tools=[add_numbers], master_key="RSRoute_test_key")
        result = agent.invoke("What is life?")
        self.assertEqual(result["content"], "OpenAI final answer")
        self.assertEqual(result["extras"], {"detail": "x"})

    @patch("rsroute.agents.openai_agent.get_org_id", return_value="org-env")
    @patch("requests.post")
    def test_invoke_preserves_string_content(self, mock_post, mock_org):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": "Plain text from OpenAI",
            "tool_calls": [],
        }
        mock_post.return_value = mock_response

        agent = GPTAgent(tools=[echo_text], master_key="RSRoute_test_key")
        result = agent.invoke("Hello")
        self.assertEqual(result["content"], "Plain text from OpenAI")

    @patch("rsroute.agents.openai_agent.get_org_id", return_value="org-env")
    @patch("requests.post")
    def test_token_accumulation_in_tool_loop(self, mock_post, mock_org):
        resp1 = MagicMock()
        resp1.json.return_value = {
            "content": "",
            "tool_calls": [{"name": "add_numbers", "args": {"a": 3, "b": 4}, "id": "call_1", "type": "tool_call"}],
            "usage_metadata": {"input_tokens": 15, "output_tokens": 6, "total_tokens": 21},
        }
        resp2 = MagicMock()
        resp2.json.return_value = {
            "content": "Result is 7",
            "tool_calls": [],
            "usage_metadata": {"input_tokens": 25, "output_tokens": 10, "total_tokens": 35},
        }
        mock_post.side_effect = [resp1, resp2]

        agent = GPTAgent(tools=[add_numbers], master_key="RSRoute_test_key")
        result = agent.invoke("3 + 4")
        self.assertEqual(result["usage_metadata"]["input_tokens"], 40)
        self.assertEqual(result["usage_metadata"]["output_tokens"], 16)
        self.assertEqual(result["usage_metadata"]["total_tokens"], 56)

    def test_aliases(self):
        self.assertIs(OpenAIAgent, GPTAgent)
        self.assertIs(ChatGPTAgent, GPTAgent)


class TestTopPRemovedOpenAI(unittest.TestCase):
    @patch("rsroute.chat_models.openai_client.get_org_id", return_value=None)
    def test_chat_gpt_no_top_p(self, mock_org):
        client = ChatGPT(master_key="RSRoute_test_key")
        self.assertNotIn("top_p", client.request_data)

    @patch("rsroute.agents.openai_agent.get_org_id", return_value=None)
    def test_gpt_agent_no_top_p(self, mock_org):
        agent = GPTAgent(tools=[add_numbers], master_key="RSRoute_test_key")
        self.assertNotIn("top_p", agent.request_data)


if __name__ == "__main__":
    unittest.main()
