"""Some Prebuilt tools to make work more easier"""

import json
import os
import subprocess
import sys
import tempfile
from typing import Optional

import requests
from ddgs import DDGS
from langchain_core.tools import tool
import wikipediaapi

from rsroute.urls import PARAMS_URL, URLS


@tool
def search_wikipedia(topic : str, language : str = "en") -> str:
    """Retrieve the full plain-text content of Wikipedia page.

    Use this tool only when the user explicitly requests information from
    Wikipedia.

    Args:
        topic: The title or subject of the Wikipedia page to look up (e.g.,
            "Python (programming language)" or "Alan Turing").
        language: The Article Language demanded e.g "en", "hi"
            Defaults to "en"

    Returns:
        str: The full text content of the matching Wikipedia page if it exists.
            If no matching page is found, returns ``"No result found for {topic}"``.
            If an error occurs during retrieval, returns the exception message as
            a string.
    """
    try:
        wiki = wikipediaapi.Wikipedia(
            user_agent="RSRoute | https://www.rsroute.freedev.app", 
            language=language
        )

        page = wiki.page(topic)

        if page.exists():
            return str(page.text) # make sure for str object only.
        else:
            return f"No result found for {topic}"

    except Exception as E:
        return str(E)


@tool
def web_search(query: str, max_result: int = 5) -> str:
    """Search the web using DuckDuckGo and return formatted search results.

    Use this tool when you need up-to-date information from the public web,
    such as current events, documentation lookups, or answers that are not in
    Wikipedia or local context.

    Args:
        query: The search query to run (for example, "latest Python release notes").
        max_result: Maximum number of results to return. Defaults to 5.

    Returns:
        str: A newline-separated list of results including title, URL, and
            snippet for each hit. Returns ``"No search results found."`` when
            there are no matches, or the exception message as a string if the
            search fails.
    """

    try:
        results = DDGS().text(
            query,
            max_results=max_result,
        )

        if not results:
            return "No search results found."

        return "\n\n".join(
            f"Title: {result.get('title', '')}\n"
            f"URL: {result.get('href', '')}\n"
            f"Snippet: {result.get('body', '')}"
            for result in results
        )
    except Exception as E:
        return str(E)


@tool
def run_command(command: str, timeout: int = 30) -> str:
    """Run a shell command in a sandboxed subprocess and return its output.

    The command is executed in an isolated temporary working directory with a
    minimal environment and a timeout to limit side effects and resource usage.

    Args:
        command: The shell command to execute (for example, ``"ls -la"`` or
            ``"echo hello"``).
        timeout: Maximum number of seconds to allow the command to run.
            Defaults to 30.

    Returns:
        str: Combined stdout/stderr output and the process exit code. If the
            command times out or fails to start, returns a descriptive error
            message.
    """
    try:
        with tempfile.TemporaryDirectory(prefix="rsroute_sandbox_") as sandbox_dir:
            env = {
                "PATH": os.environ.get("PATH", ""),
                "HOME": sandbox_dir,
                "TMPDIR": sandbox_dir,
                "LANG": os.environ.get("LANG", "C.UTF-8"),
            }
            completed = subprocess.run(
                command,
                shell=True,
                cwd=sandbox_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            stdout = completed.stdout or ""
            stderr = completed.stderr or ""
            output = stdout
            if stderr:
                output += ("\n" if output else "") + f"[stderr]\n{stderr}"
            output += ("\n" if output else "") + f"[exit_code] {completed.returncode}"
            return output.strip() or f"[exit_code] {completed.returncode}"
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds."
    except Exception as E:
        return str(E)


@tool
def run_python_code(code: str, timeout: int = 30) -> str:
    """Execute Python source code provided as a string in a sandboxed process.

    The code is written to a temporary file inside an isolated working
    directory and executed with the current Python interpreter.

    Args:
        code: Python source code to execute.
        timeout: Maximum number of seconds to allow execution. Defaults to 30.

    Returns:
        str: Combined stdout/stderr output and the process exit code, or an
            error message if execution fails or times out.
    """
    try:
        with tempfile.TemporaryDirectory(prefix="rsroute_pycode_") as sandbox_dir:
            script_path = os.path.join(sandbox_dir, "snippet.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)

            env = {
                "PATH": os.environ.get("PATH", ""),
                "HOME": sandbox_dir,
                "TMPDIR": sandbox_dir,
                "LANG": os.environ.get("LANG", "C.UTF-8"),
                "PYTHONIOENCODING": "utf-8",
            }
            completed = subprocess.run(
                [sys.executable, script_path],
                cwd=sandbox_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            stdout = completed.stdout or ""
            stderr = completed.stderr or ""
            output = stdout
            if stderr:
                output += ("\n" if output else "") + f"[stderr]\n{stderr}"
            output += ("\n" if output else "") + f"[exit_code] {completed.returncode}"
            return output.strip() or f"[exit_code] {completed.returncode}"
    except subprocess.TimeoutExpired:
        return f"Python code timed out after {timeout} seconds."
    except Exception as E:
        return str(E)


@tool
def run_python_file(file_path: str, timeout: int = 30) -> str:
    """Execute a Python file in a sandboxed subprocess.

    The target file is run with the current Python interpreter from an isolated
    temporary working directory. The file path must refer to an existing
    readable Python file.

    Args:
        file_path: Path to the Python ``.py`` file to execute.
        timeout: Maximum number of seconds to allow execution. Defaults to 30.

    Returns:
        str: Combined stdout/stderr output and the process exit code, or an
            error message if the file is missing, execution fails, or times out.
    """
    try:
        abs_path = os.path.abspath(file_path)
        if not os.path.isfile(abs_path):
            return f"Python file not found: {file_path}"

        with tempfile.TemporaryDirectory(prefix="rsroute_pyfile_") as sandbox_dir:
            env = {
                "PATH": os.environ.get("PATH", ""),
                "HOME": sandbox_dir,
                "TMPDIR": sandbox_dir,
                "LANG": os.environ.get("LANG", "C.UTF-8"),
                "PYTHONIOENCODING": "utf-8",
            }
            completed = subprocess.run(
                [sys.executable, abs_path],
                cwd=sandbox_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            stdout = completed.stdout or ""
            stderr = completed.stderr or ""
            output = stdout
            if stderr:
                output += ("\n" if output else "") + f"[stderr]\n{stderr}"
            output += ("\n" if output else "") + f"[exit_code] {completed.returncode}"
            return output.strip() or f"[exit_code] {completed.returncode}"
    except subprocess.TimeoutExpired:
        return f"Python file timed out after {timeout} seconds."
    except Exception as E:
        return str(E)


@tool
def check_server_online(timeout: int = 5) -> str:
    """Check whether the RSRoute root server is online.

    This tool always checks the root server URL defined in
    ``rsroute.urls.URLS["root"]`` and includes the server's response.

    Args:
        timeout: Request timeout in seconds. Defaults to 5.

    Returns:
        str: If the root server responds with HTTP 200, returns
            ``"Server is Online at <server_url>"`` followed by the server
            response. Otherwise returns
            ``"Server is Offline Url tried <server_url>"`` with response/error
            details when available.
    """
    url = URLS.get("root")

    def _format_response(response: requests.Response) -> str:
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                data = response.json()
                if isinstance(data, (dict, list)):
                    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)
                return str(data)
            except ValueError:
                pass
        text = response.text.strip()
        return text if text else "<empty response>"

    try:
        response = requests.get(url, timeout=timeout)
        server_response = _format_response(response)
        if response.status_code == 200:
            return (
                f"Server is Online at {url}\n"
                f"[status_code] {response.status_code}\n"
                f"[server_response]\n{server_response}"
            )
        return (
            f"Server is Offline Url tried {url}\n"
            f"[status_code] {response.status_code}\n"
            f"[server_response]\n{server_response}"
        )
    except requests.RequestException as E:
        return f"Server is Offline Url tried {url}\n[error] {E}"


@tool
def get_providers_params(provider: str, timeout: int = 5) -> str:
    """Fetch RSRoute provider parameter information for a supported provider.

    Use this tool to retrieve the provider-specific parameters exposed by the
    RSRoute server (for example, supported models/options metadata). The server
    response is expected to be a dictionary and is returned as a formatted JSON
    string.

    Allowed providers (pass one of these values as ``provider``):
        - ``"gemini"``
        - ``"mistral"``
        - ``"openrouter"``
        - ``"openai"``
        - ``"groq"``

    Args:
        provider: Provider name to query. Must be one of the allowed providers
            listed above. The value is matched case-insensitively.
        timeout: Request timeout in seconds. Defaults to 5.

    Returns:
        str: A formatted JSON string of the provider parameters returned by the
            server. If the provider is not supported, the request fails, or the
            response cannot be parsed as a dictionary, returns a descriptive
            error message.
    """
    provider_key = (provider or "").strip().lower()
    allowed_providers = list(PARAMS_URL.keys())

    if provider_key not in PARAMS_URL:
        return (
            f"Invalid provider '{provider}'. "
            f"Allowed providers: {', '.join(allowed_providers)}"
        )

    url = PARAMS_URL[provider_key]
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            return (
                f"Unexpected response type from {url}: "
                f"expected dict, got {type(data).__name__}"
            )
        return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)
    except requests.RequestException as E:
        return f"Failed to fetch provider parameters from {url}: {E}"
    except ValueError as E:
        return f"Failed to parse JSON response from {url}: {E}"
    except Exception as E:
        return str(E)