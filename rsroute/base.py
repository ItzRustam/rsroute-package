from abc import ABC
from typing import Any, Optional, Dict
import requests


class BaseEstimator(ABC):
    """Base estimator class for RSRoute chat models."""

    def __init__(
        self,
        rsroute_url: str = None,
        model: Optional[str] = None,
        timeout: int = 30,
        master_key: str = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ):
        if rsroute_url is None:
            raise AttributeError("`rsroute_url` got `None`")
        
        self.rsroute_url = rsroute_url
        self.request_data: dict[str, Any] = {}
        self.timeout = timeout

        if model is not None:
            self.request_data["model"] = model
        if master_key is not None:
            self.request_data["master_key"] = master_key
        else:
            raise ValueError("`master_key` Can't be None")
        if max_tokens is not None:
            self.request_data["max_tokens"] = max_tokens

        for key, value in kwargs.items():
            if value is not None:
                self.request_data[key] = value

    def invoke(self, query: Optional[str] = None) -> Dict[Any, Any]:
        """Invoke the model endpoint with a query."""

        request_data = self.request_data.copy()

        if query is not None:
            request_data["query"] = query

        
        try:
            return requests.post(url=self.rsroute_url, params=request_data, timeout=self.timeout).json()
        
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(
                f"RSRoute request failed ({type(exc).__name__}). "
                "Check the server URL, connectivity, and timeout."
            ) from exc
        
