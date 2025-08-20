# Web Scraper

API built with FastAPI that provides endpoints that can scrape a web page and return the content

## Build the application

```bash
poetry install
```

## Run the Application

Use `uvicorn` to run the FastAPI application:
```bash
poetry run uvicorn web_scraper.main:app --reload --port 8003
```

## Endpoints

API schema will be available at http://localhost:8003/docs