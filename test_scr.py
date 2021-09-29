
import scrapy
# Download the full page HTML to see how it renders for scrapy
# scrapy runspider test_scr.py
class TestSpider(scrapy.Spider):
    name = "test"

    start_urls = [
        "https://www.wsj.com/search?query=bitcoin&mod=searchresults_viewallresults/",
    ]

    def parse(self, response):
        filename = response.url.split("/")[-1] + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)