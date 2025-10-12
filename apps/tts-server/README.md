# TTS Server

FastAPI server that uses coqui-tts with the xtts_v2 model to take text and return a wav file.
The voices are any of the speakers of the xtts_v2 model.

To get speakers:

```

from TTS.api import TTS
tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
print(tts_model.speakers)
```


## Build the application

```bash
uv sync
```

Set the 

## Run the Application

```bash
uv run main.py --port 8080
```

In order to prevent coqui waiting to accept the TOS set the environtment variable `COQUI_TOS_AGREED=1`

example request:

```
curl -X GET "http://localhost:8080" \
     -H "Content-Type: application/json" \
     -H "Accept: audio/wav" \
     -d '{"input":"Hello, world!","voice":"Badr Odhiambo-en"}' \
     -o output.wav
```