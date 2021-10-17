import scrapy
from scrapy.loader import ItemLoader
from FiScrape.items import CNBCArtItem, \
    parse_dt, index_of_nth
from FiScrape.search import query, start_date
from ..cookies import bloom_url, parse_new_bloom_url
import json
import grequests
from bs4 import BeautifulSoup
from lxml import etree


class BloomSpider(scrapy.Spider):
    '''
    Spider for Bloomberg.
    name :  'bloomberg'
    '''
    name = "bloomberg"
    allowed_domains = ['bloomberg.com', 'cdn-mobapi.bloomberg.com']
    # domain_name ='https://www.bloomberg.com'
    query = query
    cnbc_user = None
    cnbc_pass = None
    http_user = 'user'
    http_pass = 'userpass'
    start_urls = [bloom_url]

    bloom_script="""
        function main(splash, args)
        --  splash.private_mode_enabled = false
        splash:set_user_agent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36')
        assert(splash:go(args.url))
        assert(splash:wait(5))
        --  btn = splash:select('button.RenderBioDetails-bioToggleBtn')
        splash:runjs('document.getElementsByClassName("RenderBioDetails-bioToggleBtn")[0].click()')
        splash:evaljs('document.querySelector("#div-gpt-boxinline-119696774 > script")')
        --  btn:mouse_click()
        --  btn.style.border = "1px solid #002f6c"
        assert(splash:wait(5))
        return {
            html = splash:html(),
            png = splash:png(),
            har = splash:har(),
        }
        end
    """

    # def parse(self, response):
    #     print (response.body)

    def start_requests(self):
        yield scrapy.Request(
            url=bloom_url,
            callback=self.parse,
            meta={
                'currentPage': 1
            }
        )

    # def parse(self, response):
    #     with open('initial_response.json', 'wb') as  f:
    #         f.write(response.body)

    def parse(self, response):
        response.css('html').get()
        with open('initial_response.html', 'wb') as  f:
            f.write(response.body)
        # current_page = response.request.meta['currentPage']
        # json_resp = json.loads(response.body)
        # print (json_resp)
    #     snippets = json_resp.get('results')
    #     for snippet in snippets:
    #         snippet_date = snippet.get('datePublished')
    #         if snippet_date:
    #             # print("DATE:", snippet_date)
    #             snippet_date = parse_dt(snippet_date)
    #             if snippet_date >= start_date:
    #                 loader = ItemLoader(item=CNBCArtItem())
    #                 loader.add_value('published_date', snippet_date)
    #                 loader.add_value('headline', snippet.get('cn:title'))
    #                 loader.add_value('standfirst', snippet.get('description'))
    #                 loader.add_value('article_summary', snippet.get('summary'))
    #                 loader.add_value('tags', snippet.get('cn:sectionSubType'))
    #                 loader.add_value('tags', snippet.get('cn:keyword'))
    #                 loader.add_value('tags', snippet.get('cn:type'))
    #                 loader.add_value('tags', snippet.get('section'))
    #                 article_url = snippet.get('url')
    #                 loader.add_value('article_link', article_url)
    #                 # yield loader.load_item()

    #                 article_item = loader.load_item()
    #                 request = response.follow(article_url, self.parse_article, meta={
    #                                           'article_item': article_item})
    #                 request.meta['article_item'] = article_item
    #                 if request:
    #                     yield request
    #                 else:
    #                     yield article_item

    #     last_date = snippets[9].get('datePublished')
    #     last_date = parse_dt(last_date)
    #     if last_date >= start_date:
    #         total_pages = json_resp.get('metadata').get('totalpage')
    #         # print("TOTAL PAGES:", total_pages)
    #         if current_page <= total_pages:
    #             current_page += 1
    #             # print("CURRENT PAGE:", current_page)
    #             yield scrapy.Request(
    #                 url=parse_new_bloom_url(page_number=current_page),
    #                 callback=(self.parse),
    #                 meta={
    #                     'currentPage': current_page
    #                 }
    #             )

    # def parse_article(self, response):
    #     article_item = response.meta['article_item']
    #     loader = ItemLoader(item=article_item, response=response)
    #     article_item['authors'] = {}
    #     authors = response.xpath('//div[@class="Author-authorNameAndSocial"]')
    #     bio_links = []
    #     if authors:
    #         for author in authors:
    #             auth = author.xpath(
    #                 '//div[@class="Author-authorNameAndSocial"]/a[@class="Author-authorName"]/text()').get()
    #             article_item['authors'][f'{auth}'] = {}
    #             bio_link = author.xpath(
    #                 '//div[@class="Author-authorNameAndSocial"]/a[@class="Author-authorName"]/@href').get()
    #             bio_links.append(bio_link)
    #             article_item['authors'][f'{auth}']['bio_link'] = bio_link
    #             author_twitter = author.xpath(
    #                 './/a[@class="Author-authorTwitter"]/@href').get()
    #             article_item['authors'][f'{auth}']['author_twitter'] = author_twitter
    #         print("BIO_URLS:", bio_links)
    #         resp = self.get_urls(bio_links)
    #         self.process_author(article_item, resp)

    #     article_summary = response.xpath(
    #         '//div[@class="RenderKeyPoints-list"]//li').getall()
    #     if article_summary:
    #         loader.add_value('article_summary', article_summary)
    #     image_caption = response.xpath(
    #         '//div[@class="InlineImage-imageEmbedCaption"]/text()').get()
    #     if image_caption:
    #         loader.add_value('image_caption', image_caption)
    #     article_content = response.xpath(
    #         '//div[@class="ArticleBody-articleBody"]').getall()
    #     img_credit = response.xpath(
    #         '//div[@class="InlineImage-imageEmbedCredit"]/text()').get()
    #     if article_content:
    #         if image_caption:
    #             article_content = [x.replace(image_caption, '') for x in article_content]
    #         if img_credit:
    #             article_content = [x.replace(img_credit, '') for x in article_content]
    #         loader.add_value('article_content', article_content)
    #     article_footnote = None
    #     if article_footnote:
    #         loader.add_value('article_footnote', article_footnote)
    #     article_footnote_2 = None
    #     if article_footnote_2:
    #         loader.add_value('article_footnote', article_footnote_2)
    #     yield loader.load_item()


    # def get_urls(self, bio_links):
    #     reqs = [grequests.get(bio_link) for bio_link in bio_links]
    #     resps = grequests.map(reqs)
    #     return resps

    # def process_author(self, article_item, resps):
    #     authors = article_item['authors']
    #     for (auth, response) in zip(authors.keys(), resps):
    #         page_source = BeautifulSoup(response.text, 'lxml')
    #         try:
    #             pos = page_source.find('span', attrs={'class': "RenderBioDetails-jobTitle"}).text.strip()
    #             article_item['authors'][f'{auth}']['author_position'] = pos
    #         except:
    #             pass
    #         try:
    #             author_bio = self.get_bio(response)
    #             article_item['authors'][f'{auth}']['author_bio'] = author_bio
    #         except Exception as e:
    #             try:
    #                 author_bio = page_source.find('div', attrs={'class': "RenderBioDetails-bioText"}).text
    #                 article_item['authors'][f'{auth}']['author_bio'] = author_bio
    #             except Exception as e:
    #                 print(f'error getting bio. #{e}')
    #         try:
    #             article_item['authors'][f'{auth}']['author_fb'] = page_source.find('a', attrs={
    #                 'class': 'icon-social_facebook'})['href'].strip()
    #         except:
    #             pass
    #         try:
    #             article_item['authors'][f'{auth}']['author_email'] = page_source.find('a', attrs={
    #                 'class': 'icon-social_email'})['href'].strip()
    #         except:
    #             pass
    #     return article_item

    # def get_bio(self, response):
    #     soup = BeautifulSoup(response.content, "lxml")
    #     dom = etree.HTML(str(soup))
    #     js_script = dom.xpath('//script[contains(., "locationBeforeTransitions")]/text()')
    #     # print(js_script)
    #     if js_script:
    #         txt = js_script[0]
    #         start = txt.find('modules', txt.find('modules')+1) +10
    #         end = index_of_nth(txt, 'column', 4) - 16
    #         json_string = txt[start:end]
    #         # print(json_string)
    #         try:
    #             data = json.loads(json_string)
    #             body = data.get('data').get('body')
    #             content = body.get('content')
    #             p_tags = content[0].get('children')
    #             author_bio = []
    #             for i in range(len(p_tags)):
    #                 author_bio.append(''.join(map(str, p_tags[i].get('children'))))
    #             author_bio = ''.join(author_bio).strip()
    #             return author_bio
    #         except:
    #             end = index_of_nth(txt, 'column', 5) - 16
    #             json_string = txt[start:end]
    #             data = json.loads(json_string)
    #             body = data.get('data').get('body')
    #             content = body.get('content')
    #             p_tags = content[0].get('children')
    #             author_bio = []
    #             for i in range(len(p_tags)):
    #                 author_bio.append(''.join(map(str, p_tags[i].get('children'))))
    #             author_bio = ''.join(author_bio).strip()
    #             return author_bio

    #     # js_script = response.xpath('//script[contains(., "locationBeforeTransitions")]/text()')
    #     # if js_script:
    #     #     txt = js_script.extract_first()
    #     #     start = txt.find('modules', txt.find('modules')+1) +10
    #     #     end = index_of_nth(txt, 'column', 4) - 16
    #     #     json_string = txt[start:end]
    #     #     data = json.loads(json_string)
    #     #     body = data.get('data').get('body')
    #     #     content = body.get('content')
    #     #     p_tags = content[0].get('children')
    #     #     author_bio = []
    #     #     for i in range(len(p_tags)):
    #     #         author_bio.append(''.join(map(str, p_tags[i].get('children'))))
    #     #     author_bio = ' '.join(author_bio)
    #     #     # print ("author_bio:", author_bio)
    #     #     return author_bio