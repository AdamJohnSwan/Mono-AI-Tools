import unittest

from web_scraper.config import Config
from web_scraper.scraper import Scraper

class TestScraper(unittest.TestCase):
    def test_scrape_content(self):
        html = """
        <html>
            <body>
                <div id="test1"><p>Content 1</p></div>
                <div id="test2"><p>Content 2</p></div>
            </body>
        </html>
        """
        config = Config()
        url = "http://labod.co"
        xpaths = ['//div[@id="test1"]', '//div[@id="test2"]']
        scraper = Scraper(config, url, xpaths, html=html)
        result = scraper.scrape_content(xpaths)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].xpath, '//div[@id="test1"]')
        self.assertEqual(result[0].nodes, ['<div id="test1"><p>Content 1</p></div>'])
        self.assertEqual(result[1].xpath, '//div[@id="test2"]')
        self.assertEqual(result[1].nodes, ['<div id="test2"><p>Content 2</p></div>'])

    def test_scrape_article(self):
        blog_html = """
        <html>
            <body>
                <article>
                    <h1>Blog Post Title</h1>
                    <p>This is the first paragraph of the blog post.</p>
                    <p>This is the second paragraph of the blog post.</p>
                </article>
            </body>
        </html>
        """
        config = Config()
        url = "http://exampleblog.com"
        scraper = Scraper(config, url, html=blog_html)
        result = scraper.scrape_article()
        
        self.assertIsInstance(result, str)
        self.assertIn("Blog Post Title", result)
        self.assertIn("This is the first paragraph of the blog post.", result)
        self.assertIn("This is the second paragraph of the blog post.", result)

if __name__ == '__main__':
    unittest.main()
