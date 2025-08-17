
from pydantic import BaseModel, Field
from shared.chroma.chroma_client import VectorSearchResult

class GetKnowledgeResponse(BaseModel):
    results: list[VectorSearchResult] = Field()

class CreateKnowledgeResponse(BaseModel):
    id: str = Field()

class ListCollectionsResponse(BaseModel):
    collections: list[str]