from typing import Any, Dict, Optional

from rsroute.base import BaseEstimator, get_org_id
from rsroute.urls import END_POINTS, URLS


class ChatGPT(BaseEstimator):
    """ChatGPT (ChatOpenAI) client for RSRoute."""

    def __init__(
        self,
        model: Optional[str] = None,
        master_key: Optional[str] = None,
        rsroute_url: Optional[str] = None,
        system_prompt: Optional[Any] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: int = 60,
        end_point: Optional[str] = None,
        max_retries: Optional[int] = None,
        use_response_api: Optional[bool] = None,
        organization_id: Optional[str] = None,
        **kwargs: Any,
    ):
        # Determine the target endpoint URL
        if rsroute_url is None:
            openai_url = URLS.get("openai")
        else:
            openai_url = f"{rsroute_url.rstrip('/')}/{END_POINTS.get('openai').lstrip('/')}"

        # Resolve organization_id: explicit arg > org_id alias > .env lookup
        resolved_org_id = organization_id or get_org_id()

        super().__init__(
            rsroute_url=openai_url,
            model=model,
            master_key=master_key,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            end_point=end_point,
            max_retries=max_retries,
            use_response_api=use_response_api,
            organization_id=resolved_org_id,
            **kwargs,
        )

    def invoke(self, query: Optional[Any] = None) -> Dict[Any, Any]:
        """Send a request to RSRoute OpenAI chat endpoint with the given query."""
        return super().invoke(query=query)


# Alias
ChatOpenAI = ChatGPT
