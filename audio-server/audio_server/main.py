from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from dotenv import load_dotenv

from .dtos.requests import TextToSpeechRequest

app = FastAPI(
    title="Rag Server",
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

# -------------------------------
# Routes
# -------------------------------


@app.post("/audio/speech", summary="Takes text and synthesizes it into speech.", status_code=200)
async def text_to_speech(request: TextToSpeechRequest) -> FileResponse:
    raise NotImplementedError()



@app.post("/audio/transcriptions", summary="Takes audio and transcribes it to text.", status_code=200)
async def speech_to_text(file: UploadFile):
    raise NotImplementedError()