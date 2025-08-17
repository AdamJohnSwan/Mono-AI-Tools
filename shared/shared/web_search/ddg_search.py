
from typing import Optional
from ddgs import DDGS
from .search_result import WebSearchResult

def ddg_search(query: str, limit: Optional[int] = 5) -> list[WebSearchResult]:
    with DDGS() as ddgs:
        search_results = ddgs.text(
                query,
                safesearch="off",
                max_results=limit,
                backend="duckduckgo"
            )
        return [
            WebSearchResult(
                uri=result["href"],
                title=result.get("title", ""),
                description=result.get("body", ""),
            )
            for result in search_results
        ]