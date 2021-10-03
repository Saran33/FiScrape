import scrapy
from scrapy.loader import ItemLoader
from FiScrape.items import BBCArtItem, \
    time_ago_str, join_str_lst
from FiScrape.search import query, start_date


class BBCSpider(scrapy.Spider):
    '''
    Spider for the BBC.
    name :  'bbc'
    '''
    name = "bbc"
    # allowed_domains = ['bbc.co.uk']
    # domain_name ='https://www.bbc.co.uk'
    start_urls = [f"https://www.bbc.co.uk/search?q={query}"]

    def parse(self, response):
        self.logger.info('Parse function called on {}'.format(response.url))
        article_snippets = response.xpath('//*/ul[@class="ssrcss-v19xcd-Stack e1y4nx260"]/li')

        for snippet in article_snippets:
            snippet_date = snippet.xpath('.//*[@class="ssrcss-8d0yke-MetadataStripItem e1ojgjhb1"][1]/dd/span/text()').get()
            snippet_date = time_ago_str(snippet_date)
            if snippet_date:
                if snippet_date >= start_date:
                    loader = ItemLoader(item=BBCArtItem(), selector=snippet)
                    # loader.add_css('published_date', 'div.tout-tag.d-lg-flex span::text')
                    loader.add_css('headline', 'a > span > p > span::text')
                    loader.add_xpath('standfirst', './/p/text()')
                    loader.add_css('tags', 'div > dl > div:nth-child(2) > dd > span ::text, div > dl > div:nth-child(3) > dd > span ::text')
                    article_url = snippet.css('a::attr(href)').get()
                    loader.add_value('article_link', article_url)
                    # go to the article page and pass the current collected article info
                    # self.logger.info('Get article page url')
                    article_item = loader.load_item()
                    request = response.follow(article_url, self.parse_article, meta={'article_item': article_item})
                    request.meta['article_item'] = article_item
                    if request:
                        yield request
                    else:
                        yield article_item
            else:
                pass

        next_pages = response.xpath('//*[@class="ssrcss-i7uuy0-Cluster e1ihwmse1"]/ol//a/@href').getall()
        yield from response.follow_all(next_pages, callback=self.parse)

        # last_date = response.xpath('//*[@class="ssrcss-8d0yke-MetadataStripItem e1ojgjhb1"][1]/dd/span/text()')[-1].extract()
        # last_date = time_ago_str(last_date)
        # if last_date >= start_date:
        #     # Go to next search page
        #     for a in response.xpath('//*/div[@class="ssrcss-zhhf7y-PageButtonContainer e1b2sq420"]/a').get():
        # #     for a in response.xpath('//*/div[@class="ssrcss-zhhf7y-PageButtonContainer e1b2sq420"]/a/@href').get():
        #         yield response.follow(a, callback=self.parse)

    def parse_article(self, response):
        article_item = response.meta['article_item']
        loader = ItemLoader(item=article_item, response=response)
        published_date = response.xpath('//article/header//time/@datetime').get()
        if not published_date:
            # For radio broadcasts
            published_date = response.xpath('//*/div[@class="broadcast-event__time beta"]/@content').get()
            loader.add_value('tags', 'Radio')
        if published_date:
            loader.add_value('published_date', published_date)
            article_item['authors'] = {}
            authors = response.xpath('//article/header/p')
            # bio_links = []
            if authors:
                for author in authors:
                    auth = author.xpath('.//span/strong/text()').get().replace('By ', '')
                    article_item['authors'][f'{auth}'] = {}
                    # bio_link = author.css('a::attr(href)').extract()
                    # bio_link = response.urljoin(''.join(map(str, bio_link)))
                    article_item['authors'][f'{auth}']['bio_link'] = None
                    author_position = authors.css('span::text').get()
                    if author_position:
                        article_item['authors'][f'{auth}']['author_position'] = author_position
                    else:
                        article_item['authors'][f'{auth}']['author_position'] = None
                    author_email = response.xpath(
                        '//*[@class="ssrcss-1q0x1qg-Paragraph eq5iqo00"]/a[contains(@href,"email")]/@href').getall()
                    if author_email:
                        article_item['authors'][f'{auth}']['author_email'] = join_str_lst(author_email)
                    else:
                        article_item['authors'][f'{auth}']['author_email'] = None
                    author_twitter = response.xpath(
                        '//*[@class="ssrcss-1q0x1qg-Paragraph eq5iqo00"]/a[contains(@href,"twitter")]/@href').getall()
                    if author_twitter:
                        article_item['authors'][f'{auth}']['author_twitter'] = join_str_lst(author_twitter)
                    else:
                        article_item['authors'][f'{auth}']['author_twitter'] = None
                #     bio_links.append(bio_link)
                # resp = self.get_urls(bio_links)
                # self.process_author(article_item, resp)

            article_summary = response.xpath('//article/div[@data-component="text-block"][1]/div/p/b/text()').get()
            if not article_summary:
                article_summary = response.xpath(
                    '//*/div[@class="synopsis-toggle__long"]/p[not(contains(.,"Image:"))][not(contains(.,"Photo:"))]/text()').getall()
            if article_summary:
                loader.add_value('article_summary', article_summary)
            image_caption = response.xpath('//figcaption/text()').getall()
            if not image_caption:
                image_caption = response.xpath(
                    '//*/div[@class="synopsis-toggle__long"]/p[(contains(.,"Image:")) or (contains(.,"Photo:"))]/text()').getall()
            if image_caption:
                loader.add_value('image_caption', image_caption)
            article_content = response.css(
                    'article > div[data-component=text-block] > div > p ::text, article > div[data-component=crosshead-block] > h2').getall()
            if article_content:
                loader.add_value('article_content', article_content)
            bold_text = response.css('article > div[data-component=text-block] > div > p > b ::text').getall()
            article_footnote = []
            for para in bold_text:
                if para not in article_summary:
                    article_footnote.append(para)
            if article_footnote:
                loader.add_value('article_footnote', article_footnote)
            yield loader.load_item()
        else:
            pass

