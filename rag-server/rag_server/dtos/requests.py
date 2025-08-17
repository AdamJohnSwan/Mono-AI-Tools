
from dataclasses import dataclass
from typing import Any, Optional

from pydantic import BaseModel, Field


@dataclass
class CreateKnowledgeRequest(BaseModel):
    content: str = Field(title="content", description="text content that will be added to the knowledge base.")
    metadata: dict[str, Any] = Field(default={}, title="Metadata for the text content", description="JSON describing what is in the content such as tags.")

@dataclass
class SearchKnowledgeRequest(BaseModel):
    query: str = Field(min_length=1, max_length=100)
    knowledge_bases: Optional[list[str]] = Field(description="The knowledge bases to search")
    limit: int = Field(default=10, ge=1, le=100)