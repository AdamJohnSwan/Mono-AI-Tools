import os
import wave
from pathlib import Path
from tempfile import NamedTemporaryFile
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from piper import PiperVoice, download_voices

from dotenv import load_dotenv

from .config import get_config
from .dtos.requests import TextToSpeechRequest

app = FastAPI(
    title="Audio Server",
    version="1.0.0",
    description=""
)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv() 
config = get_config()

for voice in config.available_voices:
    download_voices.download_voice(voice, config.voice_directory)

# -------------------------------
# Routes
# -------------------------------

def cleanup_audio(path: str):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

@app.post("/audio/speech", summary="Takes text and synthesizes it into speech.", status_code=200)
async def text_to_speech(request: TextToSpeechRequest) -> FileResponse:
    voice_path = Path(config.voice_directory, request.voice + ".onnx")
    if not voice_path.exists():
        raise HTTPException(status_code=400, detail="Voice not available")
    voice = PiperVoice.load(voice_path)
    # with wave.open("test.wav", "wb") as temp_file:
    #     voice.synthesize_wav(request.input, temp_file)
    temp_file = NamedTemporaryFile(mode="wb", delete=False)        
    for chunk in voice.synthesize(request.input):
        temp_file.write(chunk.audio_int16_bytes)
    temp_file.close()
    return FileResponse(
        temp_file.name,
        media_type="audio/wave",
        background=BackgroundTask(cleanup_audio, temp_file.name))


@app.post("/audio/transcriptions", summary="Takes audio and transcribes it to text.", status_code=200)
async def speech_to_text(file: UploadFile):
    raise NotImplementedError()

@app.get("/audio/speech/voices", summary="List the available voices.", status_code=200)
def list_voices():
    return config.available_voices
