# rag-server

The `rag-server` is an API built using FastAPI that provides endpoints to create knowledge bases and retrieve information from them. 

## Environment Variables 

Create a `.env` file in the project root with the required environment variables:
```plaintext
CHROMA_DB_URL=your_chroma_db_url
CHROMA_USE_SSL=True | False
CHROMA_TENANT=your_tenant or default_tenant
CHROMA_DATABASE=your_database or default_database
OLLAMA_API_URL=your_ollama_api_url
EMBEDDING_MODEL_ID=your_embedding_model_id
```

## Build the application

```bash
uv build
```

## Run the Application

Use `uvicorn` to run the FastAPI application:
```bash
uvicorn main:app --reload
```

## Endpoints

1. **List all knowledge bases**
   - Method: GET
   - Path: `/`
   - Response Model: `GetKnowledgeResponse`

2. **Add knowledge to a specific collection**
   - Method: POST
   - Path: `/{collection}`
   - Request Body: `CreateKnowledgeRequest`
   - Response Model: `CreateKnowledgeResponse`

3. **Update knowledge in a specific collection**
   - Method: PUT
   - Path: `/{collection}/{id}`
   - Request Body: `CreateKnowledgeRequest`
   - Response Model: None

4. **Delete knowledge from a specific collection**
   - Method: DELETE
   - Path: `/{collection}/{id}`
   - Response Model: None

5. **Search for knowledge within a specific collection**
   - Method: GET
   - Path: `/{collection}`
   - Query Parameters:
     - `q`: The search query (required)
     - `limit`: The number of results to return (default is 10, min is 1, max is 100)
   - Response Model: `GetKnowledgeResponse`