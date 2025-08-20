# Audio Server

API built with FastAPI that has endpoints for handling speech to text and text to speech.
The projects endpoints are meant to mimic OpenAI endpoints so that this can be used as a drop in replacement for OpenAI speech services.

## Environment Variables 

Create a `.env` file in the project root with the required environment variables:
```plaintext

```

## Build the application

```bash
poetry install
```

## Run the Application

Use `uvicorn` to run the FastAPI application:
```bash
poetry run uvicorn audio_server.main:app --reload --port 8004
```

## Endpoints

API schema will be available at http://localhost:8004/docs