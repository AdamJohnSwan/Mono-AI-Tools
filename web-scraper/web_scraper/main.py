from typing import Annotated
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_config

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

@app.get("/scrape/{url}", summary="Scrape a webpage and attempt to get the main contnet", status_code=200, )
async def scrape_webpage(url: Annotated[str, "The url of the webpage to scrape."]):
    pass