
from dataclasses import dataclass


@dataclass
class UsageReponse:
    input_tokens: int
    input_token_details: dict[str, int | str]
    output_tokens: int
    total_tokens: int

@dataclass
class SpeechToTextResponse:
    text: str
    usage: UsageReponse