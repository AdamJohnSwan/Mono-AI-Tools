#!/bin/bash
uvicorn rag-server.rag_server.main:app --host 0.0.0.0 --port 8001 &
uvicorn agentic-answers.agentic_answers.main:app --host 0.0.0.0 --port 8002 &
uvicorn web-scraper.web_scraper.main:app --host 0.0.0.0 --port 8003 &
uvicorn audio-server.audio_server.main:app --host 0.0.0.0 --port 8003 &