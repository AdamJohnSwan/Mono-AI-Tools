# Audio Server

API built with FastAPI that has endpoints for handling speech to text and text to speech.
The projects endpoints are meant to mimic OpenAI endpoints so that this can be used as a drop in replacement for OpenAI speech services.

Piper TTS is used as the text to speech. [Available voices](https://rhasspy.github.io/piper-samples/)

## Environment Variables 

Create a `.env` file in the project root with the required environment variables:
```
VOICES=string # A comma seperated list of available voices.
VOICE_DIRECTORY=string # Optional. A path to where voices will be downloaded.
VOICE_CACHE_MINUTES=int # How long to keep a voice loaded before its resources are released. Defaults to 300 seconds (5 minutes)
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