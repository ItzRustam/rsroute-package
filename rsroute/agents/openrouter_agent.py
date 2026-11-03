"""Implementation of OpenRouter Agent Integration by RSRoute"""

from typing import Any, Dict, List, Optional
import warnings

from rsroute.base import BaseEstimatorAgent
from rsroute.urls import END_POINTS, URLS
from langchain_core.tools import StructuredTool


class OpenRouterAgent(BaseEstimatorAgent):
    """OpenRouterAgent client for RSRoute."""

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
        app_title: Optional[str] = None,
        app_url: Optional[str] = None,
        app_categories: Optional[List[str]] = None,
        max_retries: Optional[int] = None,
        providers: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ):
        # Determine the target endpoint URL
        if rsroute_url is None:
            openrouter_url = URLS.get("openrouter_agent")
        else:
            openrouter_url = f"{rsroute_url.rstrip('/')}/{END_POINTS.get('openrouter_agent').lstrip('/')}"

        super().__init__(
            rsroute_url=openrouter_url,
            model=model,
            max_tool_calls=max_tool_calls,
            tools=tools,
            master_key=master_key,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            timeout=timeout,
            end_point=end_point,
            app_title=app_title,
            app_url=app_url,
            app_categories=app_categories,
            max_retries=max_retries,
            providers=providers,
            **kwargs,
        )

    def ainvoke(self, query: Optional[Any] = None) -> Dict[Any, Any]:
        """Send a request to RSRoute OpenRouter Agent endpoint with the given query."""
        return super().ainvoke(query=query)

    def invoke(self, query=None):
        """Generate response from Agent with ReAct Loop"""
        results: Dict[str, Any] = super().invoke(query)
        if not isinstance(results.get("content"), list):
            return results
        if len(results.get("content", [])) != 1:
            return results

        try:
            result = results.copy()  # Safety copy
            content: Dict[str, Any] = result.get("content")[0]
            if isinstance(content, dict) and "text" in content:
                text_result = content.get("text")
                extras = content.get("extras")

                result["content"] = text_result
                result["extras"] = extras

                return result
        except Exception as E:
            warnings.warn(f"Got Error while extracting the information, {str(E)}")

        return results


ChatOpenRouterAgent = OpenRouterAgent

