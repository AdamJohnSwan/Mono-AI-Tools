from pathlib import Path
from shared.get_env import get_env
import torch


class Config:
    def __init__(self):
        self.available_voices = [voice.strip() for voice in str(get_env("VOICES", str)).split(",")]
        if len(self.available_voices) == 0:
            raise ValueError("There are no voices configured")
        directory: str = get_env("VOICE_DIRECTORY", str, "")
        self.voice_directory = (Path(directory) if directory else Path()).resolve()
        self.cache_timeout = get_env("VOICE_CACHE_SECONDS", int, 300)
        self.is_cuda_available = torch.cuda.is_available()

def get_config():
    return Config()