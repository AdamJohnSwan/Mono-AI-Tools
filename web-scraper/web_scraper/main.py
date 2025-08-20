import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .dtos.requests import ScrapeArticleRequest
from .dtos.responses import ScrapeArticleResponse
from .config import get_config
from .scraper import Scraper

app = FastAPI(
    title="Web Scraper",
    version="1.0.0",
    description=""
)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv() 
config = get_config()

@app.post("/scrape/article", summary="Scrape a webpage and get the article", status_code=200)
async def scrape_article(request: ScrapeArticleRequest) -> ScrapeArticleResponse:
    scraper = Scraper(config, request.url)
    content = await asyncio.to_thread(scraper.scrape_article)
    return ScrapeArticleResponse(content=content)