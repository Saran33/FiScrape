
import scrapy
import scrapy
import pandas as pd
import re
# Download the full page HTML to see how it renders for scrapy
# scrapy runspider test_scr.py

class TestSpider(scrapy.Spider):
    name = "test"

    def start_requests(self):
        """Loop through a CSV of links and return the html for each page."""

        f_path = "csv_files/news_sites/btc_news_sites.csv"
        df = pd.read_csv(f_path)
        self.start_url = []
        [self.start_url.append(url) for url in df["URL"]]

        for url in self.start_url:
            self.a = 0
            self.url = url
            self.page = self.url.split("/")[-1]
            try:
                site = re.search(r'\.(.*?)\.', url).group(1)
            except:
                site = re.search(r'\//(.*?)\.', url).group(1)
            site = site.replace('-', '_')
            self.filename = f'html_files/{site}.html'

            # with open(self.filename, 'wb') as f:
            #     f.write('URL:;'+self.url+'\n')
            request = scrapy.Request(url=self.url,callback=self.parse,dont_filter = True)
            request.meta['url'] = url
            yield request

    def parse(self, response):
        self.file = response.meta['url']
        try:
            site = re.search(r'\.(.*?)\.', self.file).group(1)
        except:
            site = re.search(r'\//(.*?)\.', self.file).group(1)
        site = site.replace('-', '_')
        filename = f'html_files/{site.split("/")[-1]}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)