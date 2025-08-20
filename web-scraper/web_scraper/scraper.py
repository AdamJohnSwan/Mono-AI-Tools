from typing import Optional
import curl_cffi
from newspaper import Article
from lxml import etree

from .dtos.responses import XpathResult
from .config import Config

class Scraper:
    __html: Optional[str]
    def __init__(self, config: Config, url: str, xpaths: list[str] = [], html: Optional[str] = None ):
        self.config = config
        self.url = url
        self.xpath = xpaths
        self.__html=html

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
    
    def scrape_content(self, xpaths: list[str]) -> list[XpathResult]:
        html = self.__get_html()
        root = etree.HTML(text=html)
        values: list[XpathResult] = []
        for xpath in xpaths:
            elements = root.xpath(xpath)
            if not isinstance(elements, list):
                values.append(XpathResult(
                    xpath=xpath,
                    nodes=[],
                    error="Not valid xpath"
                ))
                continue
            nodes: list[str] = []
            for el in elements:
                if isinstance(el, str):
                    nodes.append(el)
                elif isinstance(el, bytes):
                    nodes.append(el.decode("utf-8"))
                elif etree.iselement(el):
                    nodes.append(etree.tostring(el, encoding="unicode", with_tail=False))
            values.append(XpathResult(
                xpath=xpath,
                nodes=nodes
            ))
        return values
        