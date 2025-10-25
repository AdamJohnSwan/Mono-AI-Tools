from pydantic import BaseModel


class TextToImageRequest(BaseModel):
    prompt: str
    size: str | None = None

class ImageResponseData(BaseModel):
    b64_json: str

class ImageResponse(BaseModel):
    created: int
    data: list[ImageResponseData]
