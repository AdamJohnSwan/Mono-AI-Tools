import argparse
import os
from tempfile import NamedTemporaryFile

import torch
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.background import BackgroundTask

from TTS.api import TTS

app = FastAPI(title="Text-to-Speech API", version="1.0.0")

device = "cpu"
if torch.cuda.is_available():
    device = "cuda"

try:
    tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to load TTS model: {str(e)}")

def cleanup_audio(path: str):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

class SpeechRequest(BaseModel):
    model: str = Field(description="Not in use. Model is fixed to tts_models/multilingual/multi-dataset/xtts_v2", default="tts_models/multilingual/multi-dataset/xtts_v2")
    input: str = Field(description="The text to synthesize.")
    voice: str = Field(description="The voice to use. The language is derived from last dash. e.g. Badr Odhiambo-en would be use english as the language")

@app.get("/health", summary="Health check endpoint", status_code=200)
async def health_check():
    return {"status": "ok"}

@app.post("/v1/audio/speech", summary="Takes text and synthesizes it into speech.", status_code=200)
async def text_to_speech(request: SpeechRequest):
    input_text = request.input
    voice = request.voice

    # Extract language from voice (e.g., "Badr Odhiambo-en" -> "en")
    language_parts = voice.split("-")
    language = language_parts[-1] if len(language_parts) > 1 else "en"
    
    # Generate unique filename for temporary file
    temp_file = NamedTemporaryFile(delete=False)
    temp_path = temp_file.name
    temp_file.close()
    
    # Generate speech using TTS model
    tts_model.tts_to_file(
        text=input_text,
        speaker=voice,
        language=language,
        file_path=temp_path
    )
    
    return FileResponse(
        temp_path,
        media_type="audio/wav",
        background=BackgroundTask(cleanup_audio, temp_path)
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Text-to-Speech API Server")
    parser.add_argument("--port", type=int, required=True, help="Port number to run the server on")
    
    args = parser.parse_args()
    
    if not args.port:
        print("Error: Port number is required. Use --port <port_number>")
        exit(1)
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.port)