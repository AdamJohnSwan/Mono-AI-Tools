from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, Field

@dataclass
class ScrapeArticleResponse(BaseModel):
    content: str = Field("The text content of the article.")

@dataclass
class XpathResult():
    xpath: str
    nodes: list[str]
    error: Optional[str] = None

@dataclass
class ScrapeContentResponse(BaseModel):
    content: list[XpathResult]