# Image Generation Server

OpenAI-compatible FastAPI server used for generating images.

## Environment Variables 

Create a `.env` file in the project root with the required environment variables:
```plaintext
IMAGE_MODEL_NAME=string # Name of the model ID e.g. 'black-forest-labs/FLUX.1-dev'
```

## Build the application

```bash
uv sync
```

## Run the Application

```bash
uv run main.py --port 8080
```

## Endpoints

API schema available at `http://localhost:8080/docs`

**/v1/images/generations**
- Takes a prompt and image size as parameters.
- This endpoint will only generate one image and only return base64