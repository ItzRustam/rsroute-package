from abc import ABC
import os
from typing import Any, Dict, Optional
import requests


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
        **kwargs: Any,
    ):
        if rsroute_url is None:
            raise AttributeError("`rsroute_url` got `None`")

        self.rsroute_url = rsroute_url
        self.request_data: dict[str, Any] = {}
        self.timeout = timeout

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
