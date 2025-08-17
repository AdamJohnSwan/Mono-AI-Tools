from shared.get_env import get_env
from shared.chroma.chroma_client_config import ChromaClientConfig
from shared.embedding.embedding_client_config import EmbeddingClientConfig


class Config():
    def __init__(self):
        self.chroma_config = ChromaClientConfig(
            chroma_url=get_env("CHROMA_DB_URL", str),
            use_ssl=get_env("CHROMA_USE_SSL", bool, False),
            tenant=get_env("CHROMA_TENANT", str, "default_tenant"),
            database=get_env("CHROMA_DATABASE", str, "default_database"),
            collection=get_env("CHROMA_COLLECTION", str, "default_collection")
        )
        self.embedding_config = EmbeddingClientConfig(
            ollama_api_url=get_env("OLLAMA_API_URL", str),
            model_name=get_env("EMBEDDING_MODEL_ID", str),
        )

def get_config() -> Config:
    return Config()