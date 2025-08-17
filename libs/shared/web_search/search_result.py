
from dataclasses import dataclass


@dataclass
class WebSearchResult:
    uri: str
    description: str
    title: str