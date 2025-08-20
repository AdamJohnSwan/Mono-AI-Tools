from typing import Optional
from xml.etree.ElementTree import Element
import curl_cffi
from newspaper import Article
from lxml.etree import HTMLParser, HTML


from .config import Config

class Scraper:
    __html: Optional[str]
    def __init__(self, config: Config, url: str, xpaths: list[str] = [] ):
        self.config = config
        self.url = url
        self.xpath = xpaths

    def __get_html(self) -> str:
        """
        Gets the URL content of the page.
        """
        if (not self.__html):
            response = curl_cffi.get(self.url, impersonate="chrome")
            self.__html = response.text
        return self.__html

    def scrape_article(self) -> str:
        html = self.__get_html()
        article = Article('')
        article.download(input_html=html)
        article.parse()
        return article.text
    
    def scrape_content(self, xpath: str) -> list[str]:
        html = self.__get_html()
        root = HTML(text=html, parser=HTMLParser())
        elements = root.xpath(xpath, smart_strings=False)
        if not isinstance(elements, list):
            raise ValueError("Not valid xpath.")
        values: list[str] = []
        for el in elements:
            if isinstance(el, str):
                values.append(el)
            elif isinstance(el, bytes):
                values.append(el.decode("utf-8"))
            elif isinstance(el, Element) and el.text:
                values.append(el.text)
        return values
        