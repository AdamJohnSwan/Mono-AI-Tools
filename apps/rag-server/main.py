import asyncio
from typing import Annotated
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.chroma.chroma_client import ChromaClient
from shared.embedding.embedding_client import EmbeddingClient
from shared.rag.rag_client import RagClient
from .config import get_config
from .dtos.requests import CreateKnowledgeRequest, SearchKnowledgeRequest
from .dtos.responses import CreateKnowledgeResponse, GetKnowledgeResponse

from dotenv import load_dotenv

app = FastAPI(
    title="Rag Server",
    version="1.0.0",
    description=""
)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv() 
config = get_config()
chroma_client = ChromaClient(config.chroma_config)
embedding_client = EmbeddingClient(config.embedding_config)
rag_client = RagClient(chroma_client, embedding_client)

# -------------------------------
# Routes
# -------------------------------


@app.post("/knowledge/{knowledge_base}", summary="Add document to a knowledge base.", status_code=201, )
async def add_knowledge(knowledge_base: Annotated[str, "The name of the knowledge base that will be added to."],
                        request: CreateKnowledgeRequest):
    id = await rag_client.insert_data(knowledge_base, request.content, request.metadata)
    return CreateKnowledgeResponse(id=id)

@app.put("/knowledge/{knowledge_base}/{id}", summary="Updates documents.", status_code=202)
async def update_knowledge(knowledge_base: Annotated[str,"The name of the knowledge base that will be updated."],
                     id: Annotated[str, "The ID of the entry"],
                     request: CreateKnowledgeRequest):
    await rag_client.update_data(id, knowledge_base, request.content, request.metadata)

@app.delete("/knowledge/{id}", summary="Deletes a document.", status_code=200)
async def delete_knowledge(id: Annotated[str,"The ID of the entry to delete"]):
    await asyncio.to_thread(rag_client.delete_data, id)

@app.post("/knowledge/search", summary="Searches documents across knowledge bases", status_code=200, response_model=GetKnowledgeResponse)
async def search_knowledge(request: SearchKnowledgeRequest):
    results = await rag_client.get_documents(request.query, request.knowledge_bases, request.limit)
    return GetKnowledgeResponse(
        results=results
    )
