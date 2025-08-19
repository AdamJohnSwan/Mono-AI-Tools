from dataclasses import dataclass
from chromadb import HttpClient, Where

from typing import Any, Optional, Union
from numpy.typing import NDArray

import numpy

from .chroma_client_config import ChromaClientConfig

@dataclass
class VectorItem:
    id: str
    text: str
    vector: list[int | float]
    metadata: Any

@dataclass
class VectorSearchRequest:
    vector: NDArray[Union[numpy.int32, numpy.float32]]
    where: Optional[Where]

@dataclass
class VectorSearchResult:
    id: str
    document: str
    metadata: dict[str, Optional[Union[str, int, float, bool]]]
    distance: float

class ChromaClient():
    def __init__(self, config: ChromaClientConfig):
        self.config = config
        self.client = HttpClient(
            host=config.chroma_url,
            ssl=config.use_ssl,
            tenant=config.tenant,
            database=config.database)

    def get(self, document_id: str):
        collection = self.client.get_or_create_collection(name=self.config.collection)
        if not collection:
            raise ValueError("collection not found")
        result = collection.get(ids=[document_id])
        if not result["ids"]:
            raise ValueError("document does not exist")
        return VectorSearchResult(
            id=result["ids"][0],
            document=result["documents"][0] if result["documents"] else "",
            metadata=dict(result["metadatas"][0]) if result["metadatas"] else {},
            distance=0
        )

    def search(self, request: VectorSearchRequest, limit: int = 10) -> list[VectorSearchResult]:
        collection = self.client.get_or_create_collection(name=self.config.collection)
        if not collection:
            return []
        result = collection.query(
            query_embeddings=[request.vector],
            where=request.where,
            n_results=limit,
        )
        response: list[VectorSearchResult] = []
        for i in range(len(result["ids"][0])):
            if (not result["documents"]
                or not result["metadatas"]
                or not result["distances"]):
                raise Exception("")
            response.append(VectorSearchResult(
                id=result["ids"][0][i],
                document=result["documents"][0][i],
                metadata=dict(result["metadatas"][0][i]),
                distance=result["distances"][0][i]
            ))
        return response

    def insert(self, items: list[VectorItem]):
        collection = self.client.get_or_create_collection(
            name=self.config.collection, metadata={"hnsw:space": "cosine"}
        )

        ids = [item.id for item in items]
        embeddings = [item.vector for item in items]
        metadatas = [item.metadata for item in items]
        documents = [item.text for item in items]

        collection.add(
            ids=ids,
            embeddings=embeddings, # type: ignore - a list of ints or floats is valid. The chromadb type is just wrong.
            metadatas=metadatas,
            documents=documents
        )

    def update(self, items: list[VectorItem]):
        """
        Update the items in the collection, if the items are not present, insert them. If the collection does not exist, it will be created.
        """
        collection = self.client.get_or_create_collection(
            name=self.config.collection, metadata={"hnsw:space": "cosine"}
        )

        ids = [item.id for item in items]
        documents = [item.text for item in items]
        embeddings = [item.vector for item in items]
        metadatas = [item.metadata for item in items]

        collection.update(
            ids=ids,
            documents=documents,
            embeddings=embeddings,  # type: ignore - a list of ints or floats is valid. The chromadb type is just wrong.
            metadatas=metadatas
        )

    def delete(
        self,
        ids: Optional[list[str]] = None
    ):
        """
        Delete the items from the collection based on the ids.
        """
        collection = self.client.get_or_create_collection(name=self.config.collection)
        if collection:
            collection.delete(ids=ids)
        

    def reset(self):
        pass
