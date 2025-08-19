import uuid
from typing import Any, Optional

import numpy
from ..chroma.chroma_client import ChromaClient, VectorSearchRequest, VectorSearchResult, VectorItem
from ..embedding.embedding_client import EmbeddingClient

KNOWLEDGE_BASE_KEY = "knowledge_base"

class RagClient:
    def __init__(self, chroma_client: ChromaClient, embedding_client: EmbeddingClient):
        self.chroma_client = chroma_client
        self.embedding_client = embedding_client

    async def insert_data(self, knowledge_base: str, text_content: str, metadata: dict[str, Any]):
        embedding_response = await self.embedding_client.get_embedding(text_content)
        id = str(uuid.uuid4())
        metadata[KNOWLEDGE_BASE_KEY] = knowledge_base
        vector_item = VectorItem(
            id=id,
            text=text_content,
            vector=embedding_response.embeddings,
            metadata=metadata
        )
        self.chroma_client.insert([vector_item])
        return id

    def delete_data(self, document_id: str):
        self.chroma_client.delete([document_id])

    async def update_data(self, document_id: str, knowledge_base: str, text_content: str, metadata: Any):
        embedding_response = await self.embedding_client.get_embedding(text_content)
        metadata[KNOWLEDGE_BASE_KEY] = knowledge_base
        vector_item = VectorItem(
            id=document_id,
            text=text_content,
            vector=embedding_response.embeddings,
            metadata=metadata
        )
        self.chroma_client.update([vector_item])

    async def get_documents(self, query: str, knowledge_bases: Optional[list[str]] = [], limit: int = 10) -> list[VectorSearchResult]:
        embedding_response = await self.embedding_client.get_embedding(query)
        request = VectorSearchRequest(
            vector=numpy.asarray(embedding_response.embeddings),
            where=None
        )
        if(knowledge_bases):
            request.where[KNOWLEDGE_BASE_KEY] = { # type: ignore - ignoring because pylance doesn't believe that a list of str is valid when it is.
                "$in": knowledge_bases
            }
        query_response = self.chroma_client.search(
            request,
            limit
        )
        return query_response
    