from pathlib import Path
import threading
from piper import PiperVoice
from cachetools import TTLCache

from .config import Config

class VoiceLoader:
    def __init__(self, config: Config):  # Default timeout is 5 minutes
        self.config = config
        self.cache = TTLCache[str, PiperVoice](ttl=config.cache_timeout, maxsize=100)  # Cache with a maximum size of 100 entries

    def get_voice(self, voice_name: str) -> PiperVoice:
        if voice_name in self.cache:
            return self.cache[voice_name]
        
        voice_path = Path(self.config.voice_directory, voice_name + ".onnx")
        if not voice_path.exists():
            raise ValueError("Voice not available")
        piper_voice = PiperVoice.load(voice_path, use_cuda=self.config.is_cuda_available)
        self.cache[voice_name] = piper_voice

        # Expired cache items are only removed when items are updated.
        # To make sure a voice does not stay in memory forever, the expire method is manually called after 2x the cache time.
        threading.Timer(self.config.cache_timeout * 2, self.cache.expire).start()

        return piper_voice