
from dataclasses import dataclass

@dataclass
class ChromaClientConfig:
    chroma_url: str
    use_ssl: bool
    tenant: str
    database: str
    collection: str