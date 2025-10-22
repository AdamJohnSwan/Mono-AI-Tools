import os
import uuid
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image
import io
import base64

# Initialize FastAPI app
app = FastAPI(title="Image Generation API", version="1.0.0")

# Load the model
model_id = "runwayml/stable-diffusion-v1-5"
device = "cuda" if torch.cuda.is_available() else "cpu"

try:
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    )
    pipe = pipe.to(device)
except Exception as e:
    raise RuntimeError(f"Failed to load model: {str(e)}")

# Pydantic models for request/response
class ImageRequest(BaseModel):
    prompt: str
    n: Optional[int] = 1
    size: Optional[str] = "512x512"
    response_format: Optional[str] = "url"

class ImageResponse(BaseModel):
    created: int
    data: List[dict]

# Helper function to generate image
def generate_image(prompt: str, num_images: int = 1) -> List[Image.Image]:
    images = pipe(
        prompt,
        num_images_per_prompt=num_images,
        num_inference_steps=30
    ).images
    return images

# OpenAI-compatible endpoint
@app.post("/v1/images/generations", response_model=ImageResponse)
async def create_image(request: ImageRequest):
    try:
        # Validate parameters
        if request.n < 1 or request.n > 10:
            raise HTTPException(status_code=400, detail="n must be between 1 and 10")
        
        # Generate images
        images = generate_image(request.prompt, request.n)
        
        # Convert to base64 strings if needed
        image_data = []
        for i, img in enumerate(images):
            if request.response_format == "b64_json":
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)
                img_str = base64.b64encode(buffer.getvalue()).decode()
                image_data.append({"b64_json": img_str})
            else:  # Default to URL format (using placeholder)
                image_data.append({"url": f"data:image/png;base64,{base64.b64encode(io.BytesIO().getvalue())}"})
        
        return ImageResponse(
            created=int(time.time()),
            data=image_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
