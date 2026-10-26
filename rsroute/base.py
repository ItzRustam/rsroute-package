from abc import ABC
import os
from typing import Any, Dict, Optional, List, Iterable
import requests
from langchain_core.tools import StructuredTool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from rich import print

def _load_env_file(dotenv_path: str = ".env") -> None:
    """Fallback .env file loader if python-dotenv is not installed."""
    if os.path.exists(dotenv_path):
        try:
            with open(dotenv_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v
        except Exception:
            pass


def find_master_key(master_key: Optional[str] = None) -> Optional[str]:
    """Search for rsroute_token, master_key, or rsroute_key in arguments, environment, or .env."""
    if master_key:
        return master_key

    # Attempt to load .env using python-dotenv if installed, otherwise use fallback
    try:
        from dotenv import find_dotenv, load_dotenv
        load_dotenv(find_dotenv(usecwd=True))
    except ImportError:
        _load_env_file()

    # Search candidates in priority order (both lower and upper case)
    candidates = [
        "rsroute_token", "RSROUTE_TOKEN",
        "master_key", "MASTER_KEY",
        "rsroute_key", "RSROUTE_KEY",
        "rsroute_master_key", "RSROUTE_MASTER_KEY",
    ]
    for candidate in candidates:
        val = os.getenv(candidate)
        if val:
            return val

    return None


class BaseEstimator(ABC):
    """Base estimator class for RSRoute chat models."""

    @staticmethod
    def find_master_key(master_key: Optional[str] = None) -> Optional[str]:
        """Resolve the master key from parameter, environment, or .env file."""
        return find_master_key(master_key)

    def __init__(
        self,
        rsroute_url: str = None,
        model: Optional[str] = None,
        timeout: int = 30,
        master_key: str = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[Any] = None,
        **kwargs: Any,
    ):
        if rsroute_url is None:
            raise AttributeError("`rsroute_url` got `None`")

        self.rsroute_url = rsroute_url
        self.request_data: dict[str, Any] = {}
        self.timeout = timeout


        if system_prompt is None:
            self.system_prompt = False
        elif isinstance(system_prompt, str):
            self.system_prompt = {"role": "system", "content" : system_prompt}
        elif isinstance(system_prompt, SystemMessage):
            self.system_prompt = {"role": "system", "content" : system_prompt.content}
        else:
            self.system_prompt = {"role": "system", "content" : f"{system_prompt}"}

        resolved_key = self.find_master_key(master_key)
        if resolved_key is not None:
            self.master_key = resolved_key
            self.request_data["master_key"] = resolved_key
        else:
            raise ValueError(
                "`master_key` Can't be None. Please pass master_key or set "
                "`rsroute_token`, `master_key`, or `rsroute_key` in a .env file or environment variable."
            )

        if model is not None:
            self.model = model
            self.request_data["model"] = model
        if max_tokens is not None:
            self.max_tokens = max_tokens
            self.request_data["max_tokens"] = max_tokens

        for key, value in kwargs.items():
            if value is not None:
                self.request_data[key] = value

    def invoke(self, query: Optional[Any] = None) -> Dict[Any, Any]:
        """Invoke the model endpoint with a query."""
        request_data = self.request_data.copy()

        if query is not None:
            if self.system_prompt == False:
                request_data["query"] = [
                    {"role": "user", "content": f"{query}"}
                ]
            else:
                
                request_data["query"] = [
                    self.system_prompt,
                    {
                        "role": "user",
                        "content": f"{query}"
                    }
                ]

        try:
            return requests.post(url=self.rsroute_url, json=request_data, timeout=self.timeout).json()
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(
                f"RSRoute request failed ({type(exc).__name__}). "
                "Check the server URL, connectivity, and timeout."
            ) from exc

class BaseEstimatorAgent(BaseEstimator):
    def __init__(
        self,
        rsroute_url: str = None,
        model: Optional[str] = None,
        max_tool_calls : Optional[int] = 10,
        timeout: int = 120,
        system_prompt: Optional[Any] = None,
        master_key: str = None,
        max_tokens: Optional[int] = None,
        tools: List[StructuredTool] = None,
        **kwargs: Any,
    ):

        if tools is None or len(tools) == 0:
            raise ValueError("Tools can't be Empty")

        # Safety Check
        for tool in tools:
            if not isinstance(tool, StructuredTool):
                raise TypeError("Tool must be Langchain StructuredTool")
            else:
                ...
        
        # Internal Error Probably
        if not rsroute_url.endswith("/agent"):
            raise RuntimeError(f"Agent calls can only work with `/agent` end points, endpoint get = {rsroute_url}")

        # tools information conversion 
        self.tools_info = self.__convert_tool_to_dict(tools=tools)


        super().__init__(rsroute_url=rsroute_url,
                         model=model,
                         timeout=timeout,
                         master_key=master_key,
                         max_tokens=max_tokens,
                         tools_info=self.tools_info,
                         system_prompt=system_prompt,
                         kwargs=kwargs
                         )

        # Important Info to Save
        self.max_tool_calls = max_tool_calls
        self.tools = tools

    def ainvoke(self, query = None):
        return super().invoke(query)

    def invoke(self, query = None):
        result =  super().invoke(query)
        # tools mapping 
        tools_map = self.__map_tools(tools=self.tools)
        messages = [
            self.system_prompt,
            {"role": "user", "content": f"{query}"},
            {"role": "assistant", "content": f"{result}"}
        ]

        tool_used = 0
        while result["tool_calls"]:
            if tool_used > self.max_tool_calls:
                raise BufferError(f"Agent Called More Tool than max_tool_calls which is set to {self.max_tool_calls}")

            tool_call_info = result["tool_calls"][0]


            # choosed tool
            chosen_tool = tools_map.get(tool_call_info.get("name"))

            tool_result = chosen_tool.invoke(tool_call_info.get("args"))

            messages.append(
                {
                    "role": "tool",
                    "content": f"{tool_result}",
                    "tool_call_id": tool_call_info["id"]
                }
            )

            result = super().invoke(messages)
            messages.append(
                {"role": "assistant", "content": f"{result}"}
            )

            tool_used += 1

        return result




    def __convert_tool_to_dict(self, tools: List[StructuredTool]) -> List[Dict[str, str]]:
        tools_info = []

        for tool in tools:
            tool_info = {
                "name": tool.name,
                "description": tool.description
            }

            tools_info.append(tool_info)
        
        return tools_info

    def __map_tools(self, tools: List[StructuredTool]) -> Dict[str, StructuredTool]:
        tool_map = {}

        for tool in tools:
            tool_map[tool.name] = tool

        return tool_map
    
