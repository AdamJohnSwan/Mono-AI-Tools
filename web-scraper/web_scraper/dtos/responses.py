from dataclasses import dataclass

from pydantic import BaseModel, Field

@dataclass
class ScrapeArticleResponse(BaseModel):
    content: str = Field("The text content of the article.")