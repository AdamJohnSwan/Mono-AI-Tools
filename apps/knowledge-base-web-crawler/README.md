# Knowledge Base Web Crawler

MCP tool that will crawl a url and then upload the result to an OpenWebUI knowledge base

## Environment Variables 

Create a `.env` file in the project root with the required environment variables:
```plaintext
OPENWEBUI_API_URL=string # url to the instance of OpenWebUI
OPENWEBUI_TOKEN=string # OpenWebUI API key.
```

## Build the application

```bash
uv install
```

## Run the Application

```bash
uv run main.py
```

## Tools

```
# Crawls the URL and uploads the pages as markdown to an OpenWebUI knowledge base
crawl_and_upload(url)
```