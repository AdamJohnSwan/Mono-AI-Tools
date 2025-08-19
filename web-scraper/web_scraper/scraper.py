from bs4 import BeautifulSoup, Tag
import curl_cffi

class Scraper:
    def __init__(self, url: str):
        self.url = url

    from bs4 import BeautifulSoup

    def scrape(self) -> list[Tag]:
        response = curl_cffi.get(self.url, impersonate="chrome")
        return self.__parse(response.text)

    def __parse(self, html_content: str) -> list[Tag]:
        soup = BeautifulSoup(html_content, 'html.parser')
        candidates: list[Tag] = []
        
        # List of potential main content elements
        candidate_tags = ['div.content', 'div.main', 'article', 'main', 'section', 'div.post', 'div.entry', 'div.body']
        
        for tag in candidate_tags:
            elements = soup.select(tag)
            candidates.extend(elements)  # Explicitly typing the extend method
        
        # Return the top 5 candidates
        return candidates[:5]