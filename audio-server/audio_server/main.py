import os
import wave
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from starlette.background import BackgroundTask
from piper import download_voices

from dotenv import load_dotenv

from .config import get_config
from .dtos.requests import TextToSpeechRequest
from .voice_loader import VoiceLoader

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

voice_loader = VoiceLoader(config)

# -------------------------------
# Routes
# -------------------------------
 
def cleanup_audio(path: str):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

@app.post("/audio/speech", summary="Takes text and synthesizes it into speech.", status_code=200)
async def text_to_speech(request: TextToSpeechRequest):
    if (request.voice not in config.available_voices):
        raise HTTPException(status_code=400, detail="Requested voice is not valid.")
    voice = voice_loader.get_voice(request.voice)
    if request.stream:
        def iterchunks():
            for chunk in voice.synthesize(request.input):
                yield chunk.audio_int16_bytes
        return StreamingResponse(iterchunks(), media_type="audio/wav")
    else:
        temp_file = NamedTemporaryFile(mode="wb", delete=False)
        with wave.open(temp_file.name, "wb") as wav_file:
            voice.synthesize_wav(request.input, wav_file)
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
