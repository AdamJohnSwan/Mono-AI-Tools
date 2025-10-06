import os
import re
import logging
from typing import AsyncGenerator, Optional, cast
from urllib.parse import urlparse
import aiohttp
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlResult, CrawlerRunConfig, DefaultMarkdownGenerator, PruningContentFilter
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from mcp.server.fastmcp import FastMCP

from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv() 

# Configuration for OpenWebUI API
API_URL = os.getenv("OPENWEBUI_API_URL")
TOKEN = os.getenv("OPENWEBUI_TOKEN")
MAX_CRAWL_SESSION = int(os.getenv("MAX_CRAWL_SESSIONS", 5))
if MAX_CRAWL_SESSION < 1:
    MAX_CRAWL_SESSION = 1

if not TOKEN:
    raise ValueError("OPENWEBUI_TOKEN environment variable is not set.")
if not API_URL:
    raise ValueError("OPENWEBUI_API_URL environment variable is not set.")

mcp = FastMCP("Crawler Server")

@mcp.tool()
async def crawl_and_upload(url: str, depth: int = 1) -> str:
    """
    Crawls a given URL and uploads the crawled pages.

    Args:
        url: The url to crawl.
        depth: Optional. The depth of the crawl.
    """
    # Configure a 1-level deep crawl
    browser_config = BrowserConfig(
        enable_stealth=False,
        headless=True
    )
    crawler_config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=depth,
            include_external=False
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        markdown_generator=DefaultMarkdownGenerator(
            options={
                "ignore_images": True,
            },
            content_filter=PruningContentFilter(
                threshold=0.3,
                threshold_type="dynamic",
            ),
        ),
        verbose=False,
        stream=True
    )
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=75.0,
        check_interval=1.0,
        max_session_permit=MAX_CRAWL_SESSION,
    )

    name = extract_friendly_name(url)
    knowledge_base_response = await create_knowledge_base(name, url)
    knowledge_base_id = knowledge_base_response['id']
    result_count = 0
    async with AsyncWebCrawler(config=browser_config) as crawler:
        generator = await crawler.arun_many(urls=[url], dispatcher=dispatcher, config=crawler_config)
        async for result in cast(AsyncGenerator[CrawlResult, None], generator):
            if not result.markdown:
                logger.warning(f"No markdown generated for {result.url}, skipping...")
                continue
            file_content = result.markdown
            if hasattr(result.markdown, 'fit_markdown') and result.markdown.fit_markdown:
                file_content = result.markdown.fit_markdown
            file_content = "# Source: " + result.url + "\n\n" + file_content
            file_name = extract_friendly_name(result.url) + '.md'

            # Add the file to the knowledge base
            await add_file_to_knowledge_base(knowledge_base_id, file_name, file_content)
            logger.info(f"Added file {file_name} to knowledge base {name}")
            result_count += 1
    return f"Crawled and uploaded {result_count} pages to knowledge base {name}."

async def create_knowledge_base(name: str, description: str) -> dict:
    """
    Creates a new knowledge base in OpenWebUI.

    Args:
        name (str): The name of the knowledge base.
        description (str): The description of the knowledge base.

    Returns:
        dict: The JSON response from the API containing the knowledge base ID.
    """
    return await post_request("/api/v1/knowledge/create",{
            "name": name,
            "description": description,
            "access_control": {
                "read": {"group_ids": [], "user_ids": []},
                "write": {"group_ids": [], "user_ids": []}
            }
    })

async def add_file_to_knowledge_base(knowledge_base_id: str, filename: str, file_content: str) -> None:
    """
    Adds a file to a specific knowledge base in OpenWebUI.
    """
    form_data = aiohttp.FormData()
    form_data.add_field(
        name="file",
        value=file_content.encode('utf-8'),
        filename=filename,
        content_type="application/octet-stream",
    )
    response = await post_request("/api/v1/files/", form_data=form_data)
    file_id = response['id']
    logger.info(f"Created file {filename} with ID {file_id}")
    await post_request(f"/api/v1/knowledge/{knowledge_base_id}/file/add", {"file_id": file_id} )
    logger.info(f"Added file {filename} to knowledge base {knowledge_base_id}")

async def post_request(endpoint: str, json: Optional[dict] = None, form_data: Optional[aiohttp.FormData] = None) -> dict:
    """
    Helper function to make POST requests to the OpenWebUI API.

    Args:
        data (dict): The JSON data to send in the POST request.
        endpoint (str): The API endpoint to send the request to.

    Returns:
        dict: The JSON response from the API.
    """
    async with aiohttp.ClientSession() as session:
        headers = {'Accept': 'application/json', 'Authorization': f"Bearer {TOKEN}"}
        async with session.post(f"{API_URL}{endpoint}", headers=headers, json=json, data=form_data) as response:
            return await response.json()

def extract_friendly_name(url: str) -> str:
    """
    Extracts a friendly name from a given URL.

    Args:
        url (str): The URL to extract the friendly name from.

    Returns:
        str: The friendly name extracted from the URL.
    """
        # Parse the URL
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    # Remove trailing slashes
    domain = domain.rstrip('/')
    # Split by dots to get domain parts
    domain_parts = domain.split('.')
    # Remove suffixes from the end
    common_suffixes = ['com', 'org', 'net', 'gov', 'edu', 'co', 'io', 'ai', 'app', 'dev', 'blog']
    while domain_parts and domain_parts[-1] in common_suffixes:
        domain_parts.pop()
    # Get the main domain name
    main_name = domain_parts[0] if domain_parts else domain
    
    # Get path components
    path = parsed.path.strip('/')
    path_parts = [part for part in path.split('/') if part]
    
    # Build result with context from path
    result_parts = [main_name.capitalize()]
    result_parts.extend(path_parts)
    result = ' '.join(result_parts)
    
    # Clean up the result
    result = re.sub(r'[-_]+', ' ', result)
    result = re.sub(r'([a-z])([A-Z])', r'\1 \2', result)
    result = ' '.join(word.capitalize() for word in result.split())
    
    return result

if __name__ == "__main__":
    mcp.run(transport="stdio")