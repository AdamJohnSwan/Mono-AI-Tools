
from dataclasses import dataclass
from typing import Optional
from .embedding_client_config import EmbeddingClientConfig
from ollama import AsyncClient

@dataclass
class EmbeddingResponse:
    embeddings: list[float]
    total_duration: Optional[int]
    load_duration: Optional[int]
    prompt_eval_count: Optional[int]

class EmbeddingClient:
    def __init__(self, config: EmbeddingClientConfig):
        self.model_name = config.model_name
        self.ollama_client = AsyncClient(host=config.ollama_api_url)

    async def get_embedding(self, input_text: str) -> EmbeddingResponse:
        response = await self.ollama_client.embed(
            model=self.model_name,
            input=input_text
        )
        
        return EmbeddingResponse(
            embeddings=list(response.embeddings[0]), # since this function only passes in 1 input this list will always have a length of 1
            total_duration=response.total_duration,
            load_duration=response.load_duration,
            prompt_eval_count=response.prompt_eval_count
        )