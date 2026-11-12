"""Some Prebuilt tools to make work more easier"""

from typing import Dict, Any, Tuple
from langchain_core.tools import tool
from ddgs import DDGS
import wikipediaapi


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
def web_search(query: str, max_result=5) -> str:
    """Search the web using DuckDuckGo and return relevant search results."""

    try:

        results = DDGS().text(
            query,
            max_results=max_result
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