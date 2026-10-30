from typing import Any, Dict, Optional

from rsroute.base import BaseEstimator
from rsroute.urls import END_POINTS, URLS


class ChatGroq(BaseEstimator):
    """ChatGroq client for RSRoute."""

    def __init__(
        self,
        model: Optional[str] = None,
        master_key: Optional[str] = None,
        rsroute_url: Optional[str] = None,
        system_prompt: Optional[Any] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: int = 30,
        end_point: Optional[str] = None,
        **kwargs: Any,
    ):
        # Determine the target endpoint URL
        if rsroute_url is None:
            groq_url = URLS.get("groq")
        else:
            groq_url = f"{rsroute_url.rstrip('/')}/{END_POINTS.get('groq').lstrip('/')}"

        super().__init__(
            rsroute_url=groq_url,
            model=model,
            master_key=master_key,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            end_point=end_point,
            **kwargs,
        )

    def invoke(self, query: Optional[Any] = None) -> Dict[Any, Any]:
        """Send a request to RSRoute Groq chat endpoint with the given query."""
        return super().invoke(query=query)

