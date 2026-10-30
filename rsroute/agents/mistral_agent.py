"""Implementation of Mistral Agent Integration by RSRoute"""

from typing import Any, Dict, Optional, List

from rsroute.base import BaseEstimatorAgent
from rsroute.urls import END_POINTS, URLS
from langchain_core.tools import StructuredTool


class MistralAgent(BaseEstimatorAgent):
    """MistralAgent client for RSRoute."""

    def __init__(
        self,
        model: Optional[str] = None,
        tools: List[StructuredTool] = None,
        master_key: Optional[str] = None,
        rsroute_url: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[Any] = None,
        max_tool_calls: Optional[int] = 10,
        timeout: int = 120,
        end_point: Optional[str] = None,
        **kwargs: Any,
    ):
        # Determine the target endpoint URL
        if rsroute_url is None:
            mistral_url = URLS.get("mistral_agent")
        else:
            mistral_url = f"{rsroute_url.rstrip('/')}/{END_POINTS.get('mistral_agent').lstrip('/')}"

        super().__init__(
            rsroute_url=mistral_url,
            model=model,
            max_tool_calls=max_tool_calls,
            tools=tools,
            master_key=master_key,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            timeout=timeout,
            end_point=end_point,
            **kwargs,
        )

    def ainvoke(self, query: Optional[Any] = None) -> Dict[Any, Any]:
        """Send a request to RSRoute Mistral Agent endpoint with the given query."""
        return super().ainvoke(query=query)

    def invoke(self, query=None):
        """Generate response from Agent with ReAct Loop"""
        return super().invoke(query)
