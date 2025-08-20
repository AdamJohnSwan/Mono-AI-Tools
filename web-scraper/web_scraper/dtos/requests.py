from dataclasses import dataclass

from pydantic import BaseModel, Field


@dataclass
class ScrapeArticleRequest(BaseModel):
    url: str = Field(description="The URL to scrape")
    

@dataclass
class ScrapeContentRequest(BaseModel):
    url: str = Field(description="The URL to scrape")
    xpaths: list[str] = Field(description="Xpaths of the page to retrieve.")