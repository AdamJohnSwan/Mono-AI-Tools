#!/bin/bash
poetry run uvicorn rag-server.rag_server.main:app --host 0.0.0.0 --port 8001 &
poetry run uvicorn agentic-answers.agentic_answers.main:app --host 0.0.0.0 --port 8002 &
poetry run uvicorn web-scraper.web_scraper.main:app --host 0.0.0.0 --port 8003 &
poetry run uvicorn audio-server.audio_server.main:app --host 0.0.0.0 --port 8003 &