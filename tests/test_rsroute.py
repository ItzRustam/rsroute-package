import unittest
from unittest.mock import patch, MagicMock
from langchain_core.tools import tool, StructuredTool

from rsroute.urls import URLS, END_POINTS
from rsroute.chat_models import ChatGemini, ChatMistral, ChatMistralAI, MistralAI, ChatGroq
from rsroute.agents import GeminiAgent, MistralAgent, GroqAgent
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

        self.assertEqual(END_POINTS["groq"], "/v1/groq/chat")
        self.assertEqual(END_POINTS["mistral_agent"], "/v1/mistral/agent")
        self.assertEqual(END_POINTS["groq_agent"], "/v1/groq/agent")


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


if __name__ == "__main__":
    unittest.main()
