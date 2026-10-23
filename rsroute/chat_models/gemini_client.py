from typing import Any, Optional, Dict
import requests

from rsroute.base import BaseEstimator
from rsroute.urls import END_POINTS, URLS


class ChatGemini(BaseEstimator):
    """ChatGemini client for RSRoute."""

    endpoint: str = "/v1/gemini/chat"

    def __init__(
        self,
        model: Optional[str] = None,
        master_key: str = None,
        rsroute_url: str = None,
        max_tokens: Optional[int] = None,
        timeout: int = 30,
        end_point: Optional[str] = None,
        thinking_level: Optional[Any] = None,
        thinking_budget: Optional[int] = None,
    ):
        # url to send request
        if rsroute_url is None:
            gemini_url = URLS.get("gemini")
        else:
            gemini_url = f"{rsroute_url}/{END_POINTS.get('gemini')}"

        super().__init__(
            rsroute_url=gemini_url,
            model=model,
            master_key=master_key,
            max_tokens=max_tokens,
            timeout=timeout,
            end_point=end_point,
            thinking_level=thinking_level,
            thinking_budget=thinking_budget,
        )

    def invoke(self, query: Optional[str] = None) -> Dict[Any, Any]:
        """Send a request to RSRoute Gemini chat endpoint with the given query."""
        return super().invoke(query=query)
