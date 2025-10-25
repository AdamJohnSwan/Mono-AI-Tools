import argparse
import logging
import os
import asyncio
from typing import Optional, List
from fastapi import FastAPI
from diffusers import DiffusionPipeline
from contextlib import asynccontextmanager
import torch
from PIL import Image
import io
import base64
import time
from models import ImageResponse, TextToImageRequest

from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

# Get configuration from environment variables
MODEL_NAME = os.getenv("IMAGE_MODEL_NAME")
if not MODEL_NAME:
    raise RuntimeError("IMAGE_MODEL_NAME environment variable is required")

class TextToImagePipeline:
    pipeline: Optional[DiffusionPipeline] = None
    device: str = "cpu"

    def start(self):
        if torch.cuda.is_available():
            logger.info("Loading CUDA")
            self.device = "cuda"
            self.pipeline = DiffusionPipeline.from_pretrained(
                MODEL_NAME,
                torch_dtype=torch.float16,
            ).to(device=self.device)
        else:
            raise Exception("No CUDA device available")

shared_pipeline = TextToImagePipeline()

@asynccontextmanager
async def lifespan(_app: FastAPI):
    shared_pipeline.start()
    yield


app = FastAPI(title="Image Generation API", version="1.0.0", lifespan=lifespan)

# Helper function to generate image using shared pipeline
async def generate(prompt: str) -> List[Image.Image]:
    # Create a new pipeline instance from the shared one for thread safety
    loop = asyncio.get_event_loop()
    if(shared_pipeline.pipeline == None):
        raise RuntimeError("Pipeline has not been started yet.")
    
    scheduler = shared_pipeline.pipeline.scheduler.from_config(shared_pipeline.pipeline.scheduler.config)
    pipeline = shared_pipeline.pipeline.from_pipe(shared_pipeline.pipeline,
                                                  scheduler=scheduler,
                                                  torch_dtype=torch.float16
                                                  )
    
    generator = torch.Generator(device=shared_pipeline.device)
    output = await loop.run_in_executor(None, lambda: pipeline(prompt, generator=generator)) #type: ignore
    return output.images #type: ignore

# OpenAI-compatible endpoint
@app.post("/v1/images/generations", response_model=ImageResponse)
async def image_generations(image_input: TextToImageRequest):
    # Generate image using shared pipeline (only one image at a time)
    images = await generate(image_input.prompt)
    
    # Convert to base64 strings with optimized format
    image_data = []
    for img in images:
        buffer = io.BytesIO()
        img.save(buffer, format="WebP")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        image_data.append({"b64_json": img_str})
    
    return ImageResponse(
        created=int(time.time()),
        data=image_data
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Text-to-Speech API Server")
    parser.add_argument("--port", type=int, required=True, help="Port number to run the server on")
    
    args = parser.parse_args()
    
    if not args.port:
        print("Error: Port number is required. Use --port <port_number>")
        exit(1)
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.port)
