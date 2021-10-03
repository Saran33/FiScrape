# import scrapy
# from scrapy.loader import ItemLoader
# from FiScrape.items import InsiderArtItem, \
#     convert_bi_dt
# from FiScrape.search import query, start_date
# from unicodedata import normalize
# from bs4 import BeautifulSoup
# # import random
# # from scrapy.selector import Selector
# # from scrapy.http import Request
# # import requests as rq
# import grequests


# class FnSpider(scrapy.Spider):
#     '''
#     Spider for Financial News London.
#     name :  'fn'
#     '''
#     name = "fn"
#     # allowed_domains = ['fnlondon.com']
#     # domain_name ='https://www.fnlondon.com'
#     start_urls = [f"https://www.fnlondon.com/search/{query}"]


#     def parse(self, response):
#         self.logger.info('Parse function called on {}'.format(response.url))
#         article_snippets = response.xpath('.//*[@id="l-content"]/section[@class="river-item featured-post"]')

#         for snippet in article_snippets:
#             published_date = snippet.css('div.tout-tag.d-lg-flex span::text').get()
#             published_date = convert_bi_dt(published_date)
#             if published_date >= start_date:
#                 loader = ItemLoader(item=InsiderArtItem(), selector=snippet)
#                 loader.add_css('published_date', 'div.tout-tag.d-lg-flex span::text')
#                 loader.add_xpath('headline', './/section/div[@class="tout-text-wrapper default-tout"]/h2/a/text()')
#                 loader.add_xpath('standfirst', './/section/div[@class="tout-text-wrapper default-tout"]/div[@class="tout-copy river body-regular"]/text()')
#                 loader.add_xpath('tags', './/div[@class="tout-tag d-lg-flex"]/a/text()')
#                 article_url = snippet.xpath('.//section/div[@class="tout-text-wrapper default-tout"]/h2/a/@href').get()
#                 loader.add_value('article_link', article_url)
#                 # go to the article page and pass the current collected article info
#                 # self.logger.info('Get article page url')
#                 article_item = loader.load_item()
#                 request = response.follow(article_url, self.parse_article, meta={'article_item': article_item})
#                 request.meta['article_item'] = article_item
#                 if request:
#                     yield request
#                 else:
#                     yield article_item


#         last_date = response.xpath('.//*[@id="l-content"]/section[@class="river-item featured-post"]/div/span//text()')[-1].extract()
#         last_date = convert_bi_dt(last_date)
#         if last_date >= start_date:
#             # Go to next search page
#             for a in response.xpath('.//*[@id="l-content"]/a').get():
#                 yield response.follow(a, callback=self.parse)

#     def parse_article(self, response):
#         article_item = response.meta['article_item']
#         loader = ItemLoader(item=article_item, response=response)
#         article_item['authors'] = {}
#         authors = response.css('div.news-post-source')
#         bio_links = []
#         if authors:
#             for author in authors:
#                 auth = author.css("a::text").get()
#                 article_item['authors'][f'{auth}'] = {}
#                 bio_link = author.css('a::attr(href)').extract()
#                 bio_link = response.urljoin(''.join(map(str, bio_link)))
#                 article_item['authors'][f'{auth}']['bio_link'] = bio_link
#                 bio_links.append(bio_link)
#             resp = self.get_urls(bio_links)
#             self.process_author(article_item, resp)

#         article_summary = response.css("div.col-xs-12.news-content.no-padding > ul > li:not([aria-level*='1']) ::text").getall()
#         if article_summary:
#             loader.add_value('article_summary', article_summary)
#         image_caption = response.xpath('.//figcaption/text()').getall()
#         if image_caption:
#             loader.add_value('image_caption', image_caption)
#         article_content = response.css(
#             'div.col-xs-12.news-content.no-padding > p ::text, div.col-xs-12.news-content.no-padding > p > a ::text, div.col-xs-12.news-content.no-padding > ul > li[aria-level*="1"] ::text').getall()
#         if article_content:
#             loader.add_value('article_content', article_content)
#         article_footnote = response.css('div.read-original ::text').getall()
#         if article_footnote:
#             loader.add_value('article_footnote', article_footnote)
#         yield loader.load_item()


#     def get_urls(self, bio_links):
#         reqs = [grequests.get(bio_link) for bio_link in bio_links]
#         resps = grequests.map(reqs)
#         return resps


#     def process_author(self, article_item, resps):
#         authors = article_item['authors']
#         for (auth, response) in zip(authors.keys(), resps):
#             page_source = BeautifulSoup(response.text, 'lxml')
#             try:
#                 pos = page_source.find('p', attrs={'data-test': "author-aside-title"}).text.strip()
#                 article_item['authors'][f'{auth}']['author_position'] = pos
#             except:
#                 pass
#             try:
#                 author_bio = [a.text.strip() for a in page_source.select('div.col-12.col-md-8.author-description > p')]
#                 author_bio = normalize("NFKD", ''.join(map(str, author_bio)).replace('  ', ' ').strip())
#                 article_item['authors'][f'{auth}']['author_bio'] = author_bio
#             except Exception as e:
#                 print(f'error getting bio. #{e}')
#             try:
#                 article_item['authors'][f'{auth}']['author_email'] = page_source.find('a', attrs={
#                     'class': 'author-contact-icon-link share-link email'})['href'].replace('mailto:', '').strip()
#             except:
#                 pass
#             try:
#                 article_item['authors'][f'{auth}']['author_twitter'] = page_source.find('a', attrs={
#                     'class': 'author-contact-icon-link share-link twitter'})['href'].strip()
#             except:
#                 pass
#         return article_item



# # import scrapy
# # from scrapy.loader import ItemLoader
# # from FiScrape.items import FT_ArticleItem, convert_ft_dt, InsiderArticleItem, convert_bi_dt, strp_dt #, FT_AuthorItem, AuthorItemLoader
# # from datetime import date, datetime,timedelta
# # from pytz import timezone
# # from dateutil import parser
# # from scrapy.selector import Selector
# # from FiScrape.search import query, start_date

# # class InsiderSpider(scrapy.Spider):
# #     '''
# #     Spider for Business Insider.
# #     name :  'insider'
# #     '''
# #     name = "insider"
# #     allowed_domains = ['businessinsider.com']
# #     domain_name ='https://www.businessinsider.com'
# #     start_urls = [f"https://www.businessinsider.com/s?q={query}"]

# #     def parse(self, response):
# #         self.logger.info('Parse function called on {}'.format(response.url))
# #         #article_snippets = response.xpath(".//div[@class='o-teaser o-teaser--article o-teaser--small o-teaser--has-image js-teaser']")
# #         article_snippets = response.xpath('.//*[@id="l-content"]/section[@class="river-item featured-post"]')

# #         for snippet in article_snippets:
# #             published_date = snippet.css('div.tout-tag.d-lg-flex span::text').get()
# #             published_date = convert_bi_dt(published_date)
# #             if published_date >= start_date:
# #                 loader = ItemLoader(item=InsiderArticleItem(), selector=snippet)
# #                 loader.add_css('published_date', 'div.tout-tag.d-lg-flex span::text')
# #                 loader.add_xpath('headline', './/section/div[@class="tout-text-wrapper default-tout"]/h2/a/text()')
# #                 loader.add_xpath('standfirst', './/section/div[@class="tout-text-wrapper default-tout"]/div[@class="tout-copy river body-regular"]/text()')
# #                 loader.add_xpath('tags', './/div[@class="tout-tag d-lg-flex"]/a/text()')
# #                 loader.add_xpath('article_link', './/section/div[@class="tout-text-wrapper default-tout"]/h2/a/@href')
# #                 article_item = loader.load_item()

# #                 #yield article_item

# #                 article_url = snippet.xpath('.//section/div[@class="tout-text-wrapper default-tout"]/h2/a/@href').get()
# #                 # go to the article page and pass the current collected article info
# #                 # self.logger.info('Get article page url')
# #                 yield response.follow(article_url, self.parse_article, meta={'article_item': article_item})

# #         last_date = response.xpath('.//*[@id="l-content"]/section[@class="river-item featured-post"]/div/span//text()')[-1].extract()
# #         last_date = convert_bi_dt(last_date)
# #         if  last_date >= start_date:
# #             # Go to next page
# #             for a in response.xpath('.//*[@id="l-content"]/a').get():
# #                 # self.logger.info('Go to next page')
# #                 yield response.follow(a, callback=self.parse)

# #     def parse_article(self, response):
# #         article_item = response.meta['article_item']
# #         loader = ItemLoader(item=article_item, response=response)
# #         # summary = response.css('#piano-inline-content-wrapper > div > div > ul ::text').getall()
# #         loader.add_css('article_summary', '#piano-inline-content-wrapper > div > div > ul ::text')
# #         loader.add_xpath('author_names', '//*[@class="byline-author headline-bold"]/span/a/text()')
# #         loader.add_css('article_content', '#piano-inline-content-wrapper > div > div > p ::text')
# #         loader.add_xpath('article_footnote', '//*[@class="category-tagline body-italic"]/div/p[@class="body-italic"]/text()')
# #         author_urls = response.xpath('.//*[@class="byline-link byline-author-name"]/@href').getall()
# #         # go to the author page and pass the current collected article info
# #         # self.logger.info('Get author page url')
# #         for author_url in author_urls:
# #             yield response.follow(author_url, self.parse_author, meta={'article_item': article_item}) #, loader.load_item()

# #     def parse_author(self, response):
# #         article_item = response.meta['article_item']
# #         loader = ItemLoader(item=article_item, response=response)
# #         loader.add_xpath('author_bio', './/*[@id="l-content"]/section[1]/div/div[2]/p/text()')
# #         loader.add_xpath('author_email', './/*[@class="author-contact-icon-link share-link email"]/@href')
# #         loader.add_xpath('author_twitter', './/*[@class="author-contact-icon-link share-link twitter"]/@href')
# #         yield loader.load_item()