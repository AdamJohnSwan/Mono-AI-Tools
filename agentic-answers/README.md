# Agentic Answers

API built with FastAPI that provides endpoints that will answer a prompt using multi-agent reasoning.
The agents have ability to get context using RAG and internet searches.

## Environment Variables 

Create a `.env` file in the project root with the required environment variables:
```plaintext
TASK_MODEL_ID=string # The name of the Ollama AI model to use
OLLAMA_API_URL=string # The url to the running instance of Ollama
EMBEDDING_MODEL_ID=string # The name of the Ollama AI model used for creating embeddings
MODEL_TEMPERATURE=float # Optional. Tempature of the task model

CHROMA_DB_URL=string # The url to the running Chroma instance
CHROMA_USE_SSL=bool
CHROMA_TENANT=string # Optional.
CHROMA_DATABASE=string # Optional.
```

## Build the application

```bash
poetry install
```

## Run the Application

Use `uvicorn` to run the FastAPI application:
```bash
poetry run uvicorn agentic_answers.main:app --reload --port 8002
```

## Endpoints

API schema will be available at http://localhost:8002/docs