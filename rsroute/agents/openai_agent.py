"""Implementation of OpenAI Agent Integration by RSRoute"""

from typing import Any, Dict, List, Optional
import warnings

from rsroute.base import BaseEstimatorAgent, get_org_id
from rsroute.urls import END_POINTS, URLS
from langchain_core.tools import StructuredTool


class GPTAgent(BaseEstimatorAgent):
    """GPTAgent (OpenAIAgent) client for RSRoute."""

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
        max_retries: Optional[int] = None,
        use_response_api: Optional[bool] = None,
        organization_id: Optional[str] = None,
        **kwargs: Any,
    ):
        # Determine the target endpoint URL
        if rsroute_url is None:
            openai_url = URLS.get("openai_agent")
        else:
            openai_url = f"{rsroute_url.rstrip('/')}/{END_POINTS.get('openai_agent').lstrip('/')}"

        # Resolve organization_id: explicit arg > org_id alias > .env lookup
        resolved_org_id = organization_id or get_org_id()

        super().__init__(
            rsroute_url=openai_url,
            model=model,
            max_tool_calls=max_tool_calls,
            tools=tools,
            master_key=master_key,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            timeout=timeout,
            end_point=end_point,
            max_retries=max_retries,
            use_response_api=use_response_api,
            organization_id=resolved_org_id,
            **kwargs,
        )

    def ainvoke(self, query: Optional[Any] = None) -> Dict[Any, Any]:
        """Send a request to RSRoute OpenAI Agent endpoint with the given query."""
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


# Aliases
OpenAIAgent = GPTAgent
ChatGPTAgent = GPTAgent
