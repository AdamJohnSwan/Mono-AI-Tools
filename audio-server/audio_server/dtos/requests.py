
from dataclasses import dataclass
from pydantic import BaseModel, Field

@dataclass
class TextToSpeechRequest(BaseModel):
    model: str = Field(
        default="",
        description="The name of the model to use for speech text-to-speech synthesis. Note: Currently only one model is used so this param is not needed."
    )
    input: str = Field(description="The text to synthesize.")
    voice: str = Field(description="The voice to use")