import scrapy
from scrapy.loader import ItemLoader
from FiScrape.items import ZhArtItem, \
    parse_to_utc, parse_to_os_tz, bleach_html
from FiScrape.search import query, start_date
from scrapy_splash import SplashRequest, SplashFormRequest
from itertools import count
from ln_meta_template  import zh_user, zh_pass

class ZhSpider(scrapy.Spider):
    '''
    Spider for Zero Hedge.
    name :  'zh'
    '''
    name = "zh"
    allowed_domains = ['zerohedge.com']
    # domain_name ='https://www.zerohedge.com'
    query = query
    zh_user = zh_user
    zh_pass = zh_pass
    pages_to_check = 20  # This variable sets the depth of pages to crawl, if not logged in. ZH does not sort seach results by date, unless logged in.
    url = f"https://www.zerohedge.com/search-content?qTitleBody={query}&page=0"
    # url = f'http://localhost:8050/render.html?url=https://www.zerohedge.com/search-content?qTitleBody={query}&page=0'

    next_script="""
    function main(splash, args)
        assert(splash:go(args.url))
        splash:wait((args.wait))
        splash:select('button.SimplePaginator_next__15okP'):mouse_click()
        splash:wait((args.wait))
        return splash:html()
    end
    """

    login_script = f"""
    function main(splash)
        local url = splash.args.url
        assert(splash:go(url))
        splash:wait((args.wait))

        splash:set_viewport_full()

        local search_input = splash:select('input[name=username]')   
        search_input:send_text("{zh_user}"")
        local search_input = splash:select('input[name=password]')
        search_input:send_text("{zh_pass}"")
        splash:wait((args.wait))
        local submit_button = splash:select('input[class^=BlockLogin_formSubmit__2kXfE]')
        submit_button:click()

        splash:wait((args.wait))

        return splash:html()
      end
    """

    def start_requests(self):
        # for url in self.start_urls:
        yield SplashRequest(self.url, callback=self.parse, args={'wait': 5})

    # def start_requests(self):
    #     return SplashFormRequest.from_response(self.url, callback=self.after_login, endpoint='execute',
    #     args={'lua_source': self.login_script, 'wait': 5})
    #             # 'ua': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36"})

    def after_login(self,response):
        """ This is a test function to see if login is successful."""
        print('BODY START: '+response.body+' BODY END.')
        ### Going to film list ######
        if "Username" in response.body:
            self.logger.error("##Successful Login##")

    def parse(self, response):
        self.logger.info('Parse function called on {}'.format(response.url))
        article_snippets = response.xpath('//*/div[@class="SearchResult_container__BnK-I"]')

        for snippet in article_snippets:
            snippet_date = snippet.xpath('.//div[@class="SearchResult_authorInfo__33M2f"]/span[2]/text()').get()
            if snippet_date:
                snippet_date = parse_to_os_tz(snippet_date)
                if snippet_date >= start_date:
                    loader = ItemLoader(item=ZhArtItem(), selector=snippet)
                    loader.add_xpath('headline', './/a/text()')
                    div_a = snippet.xpath('.//div[contains(@class,"SearchResult_authorInfo__33M2f")]//text()').getall()
                    div_3 = snippet.xpath('.//div[3]//text()').getall()
                    if div_a == div_3:
                        standfirst = snippet.xpath('.//div[4]//text()').getall()
                    else:
                        standfirst = div_3
                    if standfirst:
                        loader.add_value('standfirst', standfirst)
                    tags = snippet.css('div.SearchResult_category__3FL2h::text, div.tout-tag.d-lg-flex > a::text').getall()
                    if tags:
                        loader.add_value('tags', tags)
                    article_url = snippet.xpath('.//a/@href').get()
                    loader.add_value('article_link', article_url)
                    # self.logger.info('Get article page url')
                    article_item = loader.load_item()
                    request = response.follow(article_url, self.parse_article, meta={'article_item': article_item})
                    request.meta['article_item'] = article_item
                    if request:
                        yield request
                    else:
                        yield article_item


        # last_date = response.xpath('//div[@class="SearchResult_authorInfo__33M2f"]/span[2]/text()')[-1].extract()
        # last_date = parse_to_os_tz(last_date)
        # if last_date >= start_date:
        #     # Go to next search page
        #     for a in response.css('button.SimplePaginator_next__15okP').get():
        #         if a:
        #             yield SplashRequest(response.url, callback=self.parse, endpoint='execute', args={'lua_source': self.next_script, 'wait': 5}, dont_filter=True)

        for a in count(1):
            if a <= self.pages_to_check: # This number represents the depth of pages to crawl. ZH do not sort seach results by date unless logged in.
                if response:
                    url = f"https://www.zerohedge.com/search-content?qTitleBody={self.query}&page={a}"
                    yield SplashRequest(url=url, callback=self.parse)
                else:
                    break
            else:
                break

    def parse_article(self, response):
        article_item = response.meta['article_item']
        loader = ItemLoader(item=article_item, response=response)
        loader.add_xpath('published_date', '//header/footer/div[2]/text()')
        article_item['authors'] = {}
        authors = response.xpath('//article/div[3]/div[1]/p[1]/a/em/text()').get()
        if authors:
            authors = authors.replace('Authored by ', '')
            loader.add_xpath('origin_link', '//*[@id="__next"]/div/div[5]/main/article/div[3]/div[1]/p[1]/a/@href')
        elif not authors:
            authors = response.xpath('//div[@class="ContributorArticleFull_headerFooter__author__2NXEq"]/text()[2]').get()
            if not authors:
                authors = response.xpath('//*[@id="__next"]/div/div[5]/main/article/header/footer/div[1]/div/text()').get().replace('by ', '')
                if authors:
                    authors = authors.replace('by ', '')
        if authors:
            author_twitter = response.xpath('//p[last()]/em/a[contains(@href,"twitter")]/@href').get()
            if author_twitter:
                twitter_handle = response.xpath('//p[last()]/em/a[contains(@href,"twitter")]/text()').get()
                auth = twitter_handle
                article_item['authors'][f'{auth}'] = {}
                article_item['authors'][f'{auth}']['author_twitter'] = author_twitter
            else:
                auth = authors
                article_item['authors'][f'{auth}'] = {}
                article_item['authors'][f'{auth}']['author_twitter'] = None
            article_item['authors'][f'{auth}']['bio_link'] = None
            article_item['authors'][f'{auth}']['author_position'] = None
            article_item['authors'][f'{auth}']['author_bio'] = None
            article_item['authors'][f'{auth}']['author_email'] = None

        article_summary = response.xpath(
            '//article/div[3]/div[1]/ul[1]/li/p/text() | //article/div[3]/div[1]/ul[1]/li/p/a/text() | //article/div[3]/div[1]/ul[1]/li/p/strong | //article/div[3]/div[1]/ul[1]/li/p/em').getall()
        if article_summary:
            loader.add_value('article_summary', article_summary)
        body = response.css('div.NodeContent_body__2clki.NodeBody_container__1M6aJ')
        if body:
            # article_content = body.css(
            #     'p > strong, p > a::text, li > p::text, li > p > a::text, li > p > strong, li > p > em, li > p > span::text, p > u, h1, h2, h3, h4, h5, p::text').getall()
            article_content = response.css('div.NodeContent_body__2clki.NodeBody_container__1M6aJ').getall()
        if article_content:
            # article_content = [x for x in article_content if x not in article_summary]
            # article_content = [x for x in article_content if authors not in x]
            # article_content = [x for x in article_content if '<strong>Summary </strong>' not in x]
            loader.add_value('article_content', article_content)
        if body:
            image_caption = body.xpath('.//figcaption/text()').getall()
        else:
            image_caption = response.xpath('//figcaption/text()').getall()
        if image_caption:
            loader.add_value('image_caption', image_caption)
        article_footnote = response.css('div.read-original ::text').getall()
        if article_footnote:
            loader.add_value('article_footnote', article_footnote)
        yield loader.load_item()

