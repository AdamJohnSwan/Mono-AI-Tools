# Rag Server

API built with FastAPI that provides endpoints to create knowledge bases and retrieve information from them. 

## Environment Variables 

Create a `.env` file in the project root with the required environment variables:
```plaintext
CHROMA_DB_URL=string # url to the running instance of ChromaDB
CHROMA_USE_SSL=bool # Optional.
CHROMA_TENANT=string # Optional.
CHROMA_DATABASE=string # Optional.
OLLAMA_API_URL=string # url to the running instance of Ollama
EMBEDDING_MODEL_ID=string # The embedding model to use.
```

## Build the application

```bash
poetry install
```

## Run the Application

Use `uvicorn` to run the FastAPI application:
```bash
poetry run uvicorn rag_server.main:app --reload --port 8002
```

## Endpoints

API schema will be available at http://localhost:8001/docs