from typing import Any, Dict, Optional

from rsroute.base import BaseEstimator
from rsroute.urls import END_POINTS, URLS


class ChatGemini(BaseEstimator):
    """ChatGemini client for RSRoute."""

    def __init__(
        self,
        model: Optional[str] = None,
        master_key: Optional[str] = None,
        rsroute_url: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[Any] = None,
        timeout: int = 30,
        end_point: Optional[str] = None,
        thinking_level: Optional[Any] = None,
        thinking_budget: Optional[int] = None,
        **kwargs: Any,
    ):
        # Determine the target endpoint URL
        if rsroute_url is None:
            gemini_url = URLS.get("gemini")
        else:
            gemini_url = f"{rsroute_url.rstrip('/')}/{END_POINTS.get('gemini').lstrip('/')}"

        super().__init__(
            rsroute_url=gemini_url,
            model=model,
            master_key=master_key,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            timeout=timeout,
            end_point=end_point,
            thinking_level=thinking_level,
            thinking_budget=thinking_budget,
            **kwargs,
        )

    def invoke(self, query: Optional[Any] = None) -> Dict[Any, Any]:
        """Send a request to RSRoute Gemini chat endpoint with the given query."""
        return super().invoke(query=query)
