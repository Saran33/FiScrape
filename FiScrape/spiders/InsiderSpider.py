
import scrapy
from scrapy.loader import ItemLoader
from FiScrape.items import FT_ArticleItem, convert_ft_dt, InsiderArticleItem, convert_bi_dt, strp_dt #, FT_AuthorItem, AuthorItemLoader
from datetime import date, datetime,timedelta
from pytz import timezone
from dateutil import parser
from scrapy.selector import Selector
from FiScrape.search import query, start_date

class InsiderSpider(scrapy.Spider):
    '''
    Spider for Business Insider.
    name :  'insider'
    '''
    name = "insider"
    allowed_domains = ['businessinsider.com']
    domain_name ='https://www.businessinsider.com'
    start_urls = [f"https://www.businessinsider.com/s?q={query}"]

    def parse(self, response):
        self.logger.info('Parse function called on {}'.format(response.url))
        #article_snippets = response.xpath(".//div[@class='o-teaser o-teaser--article o-teaser--small o-teaser--has-image js-teaser']")
        article_snippets = response.xpath('.//*[@id="l-content"]/section[@class="river-item featured-post"]')

        for snippet in article_snippets:
            published_date = snippet.css('div.tout-tag.d-lg-flex span::text').get()
            published_date = convert_bi_dt(published_date)
            if published_date >= start_date:
                loader = ItemLoader(item=InsiderArticleItem(), selector=snippet)
                loader.add_css('published_date', 'div.tout-tag.d-lg-flex span::text')
                loader.add_xpath('headline', './/section/div[@class="tout-text-wrapper default-tout"]/h2/a/text()')
                loader.add_xpath('standfirst', './/section/div[@class="tout-text-wrapper default-tout"]/div[@class="tout-copy river body-regular"]/text()')
                loader.add_xpath('tags', './/div[@class="tout-tag d-lg-flex"]/a/text()')
                loader.add_xpath('article_link', './/section/div[@class="tout-text-wrapper default-tout"]/h2/a/@href')
                article_item = loader.load_item()

                #yield article_item

                article_url = snippet.xpath('.//section/div[@class="tout-text-wrapper default-tout"]/h2/a/@href').get()
                # go to the article page and pass the current collected article info
                # self.logger.info('Get article page url')
                yield response.follow(article_url, self.parse_article, meta={'article_item': article_item})

        last_date = response.xpath('//*[@id="l-content"]/section[@class="river-item featured-post"]/div/span//text()')[-1].extract()
        last_date = convert_bi_dt(last_date)
        if  last_date >= start_date:
            # Go to next page
            for a in response.xpath('//*[@id="l-content"]/a').get():
                # self.logger.info('Go to next page')
                yield response.follow(a, callback=self.parse)

    def parse_article(self, response):
        article_item = response.meta['article_item']
        loader = ItemLoader(item=article_item, response=response)
        # summary = response.css('#piano-inline-content-wrapper > div > div > ul ::text').getall()
        loader.add_css('article_summary', '#piano-inline-content-wrapper > div > div > ul ::text')
        loader.add_xpath('author_names', '//*[@class="byline-author headline-bold"]/span/a/text()')
        loader.add_css('article_content', '#piano-inline-content-wrapper > div > div > p ::text')
        loader.add_xpath('article_footnote', '//*[@class="category-tagline body-italic"]/div/p[@class="body-italic"]/text()')
        author_urls = response.xpath('//*[@class="byline-link byline-author-name"]/@href').getall()
        # go to the author page and pass the current collected article info
        # self.logger.info('Get author page url')
        for author_url in author_urls:
            yield response.follow(author_url, self.parse_author, meta={'article_item': article_item}) #, loader.load_item()

    def parse_author(self, response):
        article_item = response.meta['article_item']
        loader = ItemLoader(item=article_item, response=response)
        loader.add_xpath('author_bio', './/*[@id="l-content"]/section[1]/div/div[2]/p/text()')
        loader.add_xpath('author_email', './/*[@class="author-contact-icon-link share-link email"]/@href')
        loader.add_xpath('author_twitter', './/*[@class="author-contact-icon-link share-link twitter"]/@href')
        yield loader.load_item()
