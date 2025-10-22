import os
import asyncio
import random
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image
import io
import base64
import time

# Initialize FastAPI app
app = FastAPI(title="Image Generation API", version="1.0.0")

# Get configuration from environment variables
MODEL_NAME = os.getenv("IMAGE_MODEL_NAME")
if not MODEL_NAME:
    raise RuntimeError("IMAGE_MODEL_NAME environment variable is required")

IMAGE_SAVE_PATH = os.getenv("IMAGE_SAVE_PATH")

# Global shared pipeline
shared_pipeline = None

# Load the model once when the app starts
device = "cuda" if torch.cuda.is_available() else "cpu"

try:
    shared_pipeline = StableDiffusionPipeline.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    )
    shared_pipeline = shared_pipeline.to(device)
except Exception as e:
    raise RuntimeError(f"Failed to load model: {str(e)}")

# Pydantic models for request/response
class TextToImageInput(BaseModel):
    prompt: str

class ImageResponse(BaseModel):
    created: int
    data: List[dict]

# Helper function to generate image using shared pipeline
async def generate_image_with_shared_pipeline(prompt: str, num_images: int = 1) -> List[Image.Image]:
    # Create a new pipeline instance from the shared one for thread safety
    loop = asyncio.get_event_loop()
    
    # Create a new pipeline with the same configuration but fresh scheduler
    pipeline = StableDiffusionPipeline.from_pipe(shared_pipeline)
    
    # Set up generator with random seed
    generator = torch.Generator(device=device)
    generator.manual_seed(random.randint(0, 10000000))
    
    # Generate images asynchronously
    output = await loop.run_in_executor(
        None, 
        lambda: pipeline(prompt, generator=generator, num_images_per_prompt=num_images, num_inference_steps=30)
    )
    
    return output.images

# OpenAI-compatible endpoint
@app.post("/v1/images/generations", response_model=ImageResponse)
async def generate_image(image_input: TextToImageInput):
    try:
        # Generate image using shared pipeline (only one image at a time)
        images = await generate_image_with_shared_pipeline(image_input.prompt, 1)
        
        # Convert to base64 strings
        image_data = []
        for img in images:
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            img_str = base64.b64encode(buffer.getvalue()).decode()
            image_data.append({"b64_json": img_str})
        
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
