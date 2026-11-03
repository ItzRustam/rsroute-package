from typing import Any, Dict, List, Optional

from rsroute.base import BaseEstimator
from rsroute.urls import END_POINTS, URLS


class ChatOpenRouter(BaseEstimator):
    """ChatOpenRouter client for RSRoute."""

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
        app_title: Optional[str] = None,
        app_url: Optional[str] = None,
        app_categories: Optional[List[str]] = None,
        max_retries: Optional[int] = None,
        providers: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ):
        # Determine the target endpoint URL
        if rsroute_url is None:
            openrouter_url = URLS.get("openrouter")
        else:
            openrouter_url = f"{rsroute_url.rstrip('/')}/{END_POINTS.get('openrouter').lstrip('/')}"

        super().__init__(
            rsroute_url=openrouter_url,
            model=model,
            master_key=master_key,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            end_point=end_point,
            app_title=app_title,
            app_url=app_url,
            app_categories=app_categories,
            max_retries=max_retries,
            providers=providers,
            **kwargs,
        )

    def invoke(self, query: Optional[Any] = None) -> Dict[Any, Any]:
        """Send a request to RSRoute OpenRouter chat endpoint with the given query."""
        return super().invoke(query=query)


OpenRouter = ChatOpenRouter

