from dataclasses import dataclass

@dataclass
class EmbeddingClientConfig:
    ollama_api_url: str
    model_name: str
