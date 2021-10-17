import scrapy
from scrapy.loader import ItemLoader
from FiScrape.items import ReutersArtItem, \
    parse_dt, index_of_nth
from FiScrape.search import query, start_date
from ..cookies import reuters_api, parse_new_reut_url
import json
import grequests
from bs4 import BeautifulSoup
from lxml import etree
# from collections import defaultdict


class ReutersSpider(scrapy.Spider):
    '''
    Spider for Reuters.
    name :  'reuters'
    '''
    name = "reuters"
    allowed_domains = ['reuters.com']
    # domain_name ='https://www.reuters.com'
    query = query
    reut_user = None
    reut_pass = None
    http_user = 'user'
    http_pass = 'userpass'
    start_urls = [reuters_api]

    # def parse(self, response):
    #     print (response.body)

    def start_requests(self):
        yield scrapy.Request(
            url=reuters_api,
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
        snippets = json_resp.get('result').get('articles')
        for snippet in snippets:
            snippet_date = snippet.get('published_time')
            if snippet_date:
                # print("DATE:", snippet_date)
                snippet_date = parse_dt(snippet_date)
                if snippet_date >= start_date:
                    loader = ItemLoader(item=ReutersArtItem())
                    loader.add_value('published_date', snippet_date)
                    loader.add_value('headline', snippet.get('title'))
                    loader.add_value('standfirst', snippet.get('description'))
                    loader.add_value('tags', snippet.get('primary_tag').get('description'))
                    try:
                        image_caption = snippet.get('thumbnail').get('caption')
                    except:
                        image_caption = None
                    loader.add_value('image_caption', image_caption)
                    article_url = snippet.get('canonical_url')
                    article_url = response.urljoin(''.join(map(str, article_url)))
                    loader.add_value('article_link', article_url)
                    # yield loader.load_item()

                    article_item = loader.load_item()
                    response.meta['article_item'] = article_item
                    article_item = response.meta['article_item']
                    
                    article_item['authors'] = {}
                    bio_links = []
                    authors = snippet.get('authors')
                    if authors:
                        for author in authors:
                            auth = author.get('name')
                            article_item['authors'][f'{auth}'] = {}
                            bio_link = author.get('topic_url')
                            bio_link = response.urljoin(''.join(map(str, bio_link)))
                            bio_links.append(bio_link)
                            try:
                                article_item['authors'][f'{auth}']['bio_link'] = bio_link
                            except:
                                pass
                            author_email = author.get('id')
                            try:
                                article_item['authors'][f'{auth}']['author_email'] = author_email
                            except:
                                pass
                            social_links = author.get('social_links')
                            if social_links:
                                for social in social_links:
                                    if social.get('site') == 'twitter':
                                         author_twitter = social.get('url') 
                                         article_item['authors'][f'{auth}']['author_twitter'] = author_twitter
                                    if social.get('site') == 'linkedin':
                                        author_linkedin = social.get('url') 
                                        article_item['authors'][f'{auth}']['author_linkedin'] = author_linkedin
                                    if social.get('site') == 'facebook':
                                        author_fb = social.get('url') 
                                        article_item['authors'][f'{auth}']['author_fb'] = author_fb
                        resp = self.get_urls(bio_links)
                        self.process_author(article_item, resp)
                                        
                    request = response.follow(article_url, self.parse_article, meta={
                                              'article_item': article_item})
                    request.meta['article_item'] = article_item
                    if request:
                        yield request
                    else:
                        yield article_item

        last_date = snippets[-1].get('published_time')
        last_date = parse_dt(last_date)
        if last_date >= start_date:
            total_snippets = json_resp.get('result').get('pagination').get('total_size')
            per_page = json_resp.get('result').get('pagination').get('expected_size')
            # print("TOTAL PAGES:", total_snippets)
            if (current_page * per_page) <= total_snippets:
                current_page += 1
                # print("CURRENT PAGE:", current_page)
                yield scrapy.Request(
                    url=parse_new_reut_url(reuters_api, page_number=current_page),
                    callback=(self.parse),
                    meta={
                        'currentPage': current_page
                    }
                )

    def parse_article(self, response):
        article_item = response.meta['article_item']
        loader = ItemLoader(item=article_item, response=response)
        article_summary = response.xpath('//ul[contains(@class, "Summary")]//li').getall()
        if article_summary:
            loader.add_value('article_summary', article_summary)
        image_caption = response.xpath('//p[@id="primary-image-caption"]//text()').get()
        if image_caption:
            loader.add_value('image_caption', image_caption)
        article_content = response.xpath('//article//p[contains(@data-testid, "paragraph")]').getall()
        if article_content:
            loader.add_value('article_content', article_content)
        article_footnote = response.xpath('//article//span[contains(@class, "SignOff")]/text()').getall()
        if article_footnote:
            loader.add_value('article_footnote', article_footnote)
        yield loader.load_item()


    def get_urls(self, bio_links):
        reqs = [grequests.get(bio_link) for bio_link in bio_links]
        resps = grequests.map(reqs)
        return resps


    def process_author(self, article_item, resps):
        authors = article_item['authors']
        for (auth, response) in zip(authors.keys(), resps):
            soup = BeautifulSoup(response.content, "lxml")
            dom = etree.HTML(str(soup))
            js_script = dom.xpath('//script[contains(., "window.Fusion")]/text()')
            if js_script:
                try:
                    txt = str(js_script)
                    author_bio = self.get_bio(txt, auth)
                    article_item['authors'][f'{auth}']['author_bio'] = author_bio
                except Exception as e:
                    print(f'ERROR getting bio. #{e}')
        return article_item

    # def get_bio(self, txt):
    #     start = txt.find('description') +len('description')+3
    #     end = txt[start:].find('",', ) +start-1
    #     author_bio = txt[start:end].strip()
    #     return author_bio

    def get_bio(self, txt, auth):
        start = txt.find('topics') +len('topics')+3
        end = txt[start:].find('entity', ) +start-3
        author_string = txt[start:end]
        author_string = author_string.replace(r'\\"', '').replace(r'\\', '')
        json_author = json.loads(author_string)
        if json_author.get('name') == auth:
            author_bio = json_author.get('description')
        else:
            author_bio = None
        return author_bio