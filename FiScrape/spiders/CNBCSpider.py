import scrapy
from scrapy.loader import ItemLoader
from FiScrape.items import CNBCArtItem, \
    parse_dt
from FiScrape.search import query, start_date
from scrapy_splash import SplashRequest, SplashFormRequest
from itertools import count
from ..cookies import CNBC_URL, parse_new_cnbc_url
import json
import grequests

class CNBCSpider(scrapy.Spider):
    '''
    Spider for CNBC.
    name :  'cnbc'
    '''
    name = "cnbc"
    allowed_domains = ['cnbc.com', 'api.queryly.com']
    # domain_name ='https://www.cnbc.com'
    query = query
    cnbc_user = None
    cnbc_pass = None
    http_user = 'user'
    http_pass = 'userpass'
    pages_to_check = 10  # This variable sets the depth of pages to crawl, if not logged in. ZH does not sort seach results by date, unless logged in.
    # url = f"https://www.cnbc.com/search/?query={query}&qsearchterm={query}"
    start_urls = [CNBC_URL]

    # def parse(self, response):
    #     print (response.body)

    def start_requests(self):
        yield scrapy.Request(
            url=CNBC_URL,
            callback=self.parse,
            meta={
                'currentPage': 1
            }
        )

    # def parse(self, response):
    #     with open('initial_response.json', 'wb') as  f:
    #         f.write(response.body)

    def parse(self, response):
        current_page = response.request.meta['currentPage']
        json_resp = json.loads(response.body)
        # print (json_resp)
        snippets = json_resp.get('results')
        for snippet in snippets:
            snippet_date = snippet.get('datePublished')
            if snippet_date:
                print("DATE:", snippet_date)
                snippet_date = parse_dt(snippet_date)
                if snippet_date >= start_date:
                    loader = ItemLoader(item=CNBCArtItem())
                    loader.add_value('published_date', snippet_date)
                    loader.add_value('headline', snippet.get('cn:title'))
                    loader.add_value('standfirst', snippet.get('description'))
                    loader.add_value('article_summary', snippet.get('summary'))
                    loader.add_value('tags', snippet.get('cn:sectionSubType'))
                    loader.add_value('tags', snippet.get('cn:keyword'))
                    loader.add_value('tags', snippet.get('cn:type'))
                    loader.add_value('tags', snippet.get('section'))
                    article_url = snippet.get('url')
                    loader.add_value('article_link', article_url)
                    # yield loader.load_item()

                    article_item = loader.load_item()
                    request = response.follow(article_url, self.parse_article, meta={'article_item': article_item})
                    request.meta['article_item'] = article_item
                    if request:
                        yield request
                    else:
                        yield article_item

        last_date = snippets[9].get('datePublished')
        last_date = parse_dt(last_date)
        if last_date >= start_date:
            total_pages = json_resp.get('metadata').get('totalpage')
            # print("TOTAL PAGES:", total_pages)
            if current_page <= total_pages:
                current_page += 1
                # print("CURRENT PAGE:", current_page)
                yield scrapy.Request(
                    url=parse_new_cnbc_url(CNBC_URL, page_number=current_page),
                    callback=(self.parse),
                    meta={
                        'currentPage': current_page
                    }
                )

    def parse_article(self, response):
        article_item = response.meta['article_item']
        loader = ItemLoader(item=article_item, response=response)
        article_item['authors'] = {}
        authors = response.css("a.n-content-tag--author")
        bio_links = []
        if authors:
            for author in authors:
                auth = author.css("a.n-content-tag--author::text").get()
                article_item['authors'][f'{auth}'] = {}
                bio_link = author.css("a.n-content-tag--author::attr(href)").extract()
                bio_link = response.urljoin(''.join(map(str, bio_link)))
                article_item['authors'][f'{auth}']['bio_link'] = bio_link
                bio_links.append(bio_link)
            resp = self.get_urls(bio_links)
            self.process_author(article_item, resp)

        article_summary = response.xpath('.//*[@class="o-topper__standfirst"]/text()').get()
        if article_summary:
            loader.add_value('article_summary', article_summary)
        image_caption = response.xpath('//*[@id="site-content"]/div[1]/figure/figcaption/text()').getall()
        if image_caption:
            loader.add_value('image_caption', image_caption)
        article_content = response.xpath(
            '//*[contains(@class, "article__content-body n-content-body js-article__content-body")]//text()[not(ancestor::*[@class="n-content-layout__container"])]').getall()
        if article_content:
            loader.add_value('article_content', article_content)
        article_footnote = response.xpath('//*[contains(@class, "article__content-body n-content-body js-article__content-body")]/p[1]/*[self::em or self::a]//text()[not(ancestor::*[@class="n-content-layout__container"])]').getall()
        if article_footnote:
            loader.add_value('article_footnote', article_footnote)
        article_footnote_2 = response.xpath('.//*[@id="site-content"]/div[3]/div[2]/p[last()-1]/em/text()').get()
        if article_footnote_2:
            loader.add_value('article_footnote', article_footnote_2)
        yield loader.load_item()


    def get_urls(self, bio_links):
        reqs = [grequests.get(bio_link) for bio_link in bio_links]
        resps = grequests.map(reqs)
        return resps


    def process_author(self, article_item, resps):
        authors = article_item['authors']
        for (auth, response) in zip(authors.keys(), resps):
            page_source = BeautifulSoup(response.text, 'lxml')
            try:
                pos = page_source.find('div', attrs={'class': "sub-header__strapline"}).text.strip()
                article_item['authors'][f'{auth}']['author_position'] = pos
            except:
                pass
            try:
                author_bio = page_source.find('div', attrs={'class': "sub-header__description"}).text
                author_bio = normalize("NFKD", ''.join(map(str, author_bio)).replace('  ', ' ').strip())
                article_item['authors'][f'{auth}']['author_bio'] = author_bio
            except Exception as e:
                print(f'error getting bio. #{e}')
            try:
                article_item['authors'][f'{auth}']['author_email'] = page_source.find('a', attrs={
                    'data-trackable': 'send-email'})['href'].replace('mailto:', '').strip()
            except:
                pass
            try:
                article_item['authors'][f'{auth}']['author_twitter'] = page_source.find('a', attrs={
                    'data-trackable': 'twitter-page'})['href'].strip()
            except:
                pass
        return article_item