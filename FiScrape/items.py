# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

#import scrapy

from scrapy.item import Item, Field
#from scrapy.loader.processors import MapCompose, TakeFirst
from itemloaders.processors import MapCompose, TakeFirst, Compose, Join, Identity
from itemloaders import ItemLoader
from datetime import datetime
from dateutil import parser
from datetime import date, datetime,timedelta
from pytz import timezone
from dateutil import parser
from unicodedata import normalize

def strp_dt(text):
    """
    convert string '1932-03-17' to Python date, add utc timezone.
    """
    try:
        dt = datetime.strptime(text, "%Y-%m-%d")
    except:
        dt = parser.parse(text)
    dt = timezone.utc.localize(dt)
    return dt

def remove_articles(text):
    # strip the unicode articles
    #text = normalize("NFKD", text.strip(u'\u201c'u'\u201d'))
    text = normalize("NFKD",' '.join(map(str, text)).replace('  ', ' ').strip())
    return text

def remove_space(text):
    # strip the unicode articles
    text = text.replace('  ', ' ')
    # .lstrip()
    # .rstrip()
    # For X- path, you can also use: normalize-space
    return text

def extract_headline(text):
    #text = "".join(text)
    #text = text.strip(u'\u201c'u'\u201d')
    text = text.replace('  ', ' ')
    return text

def extract_standfirst(text):
    #text =  "".join(text)
    text = text.replace('\n\t\t\t\t\t\t\n\t\t\t\t\t\t', ' ').replace('...“', '').replace('”...', '.').replace('...', '').replace('.', '. ').replace(',', ', ').replace('  ', ' ').replace('   ', ' ')
    #text = text.strip(u'\u201c'u'\u201d')
    return text

def add_dots(text):
    return text + '...'

def clean_text(text):
    text = text.strip().replace("  ", " ").replace('  ', ' ').replace('  ', ' ')
    text = ' '.join(text.split())
    text = text.replace(' .', '. ').replace(' ,', ',')
    text = (text + '...').replace(' ...', '...').replace('......', '...')
    text = text.replace('?...', '?').replace('!...', '!').replace('-...', '-')
    text = text.replace('. .', '.').strip()
    text = text.replace(':', ': ').replace(':  ', ': ').replace(' ;', ';')
    text = text.replace('...', '... ').replace(' .', '... ').strip()
    text = text.replace('“ ', '"').replace(' ”','"').replace(" ’", "'").replace(" ’", "'")
    text = text.strip().replace("  ", " ").replace('  ', ' ').replace('  ', ' ')
    text = text.replace(' ... ..', '...').replace('......', '...').replace('..... ..', '...')
    text = text.replace('......', '...').replace('....', '...')
    text = text.replace("‘", "'").replace("’", "'").replace('“', '"').replace('”', '"')
    text = text.replace('  ', ' ')
    return text

def convert_date(text):
    """
    convert string 'March 17, 1932' to Python date
    """
    try:
        dt = datetime.strptime(text, '%B %d, %Y')
    except:
        dt = parser.parse(text)
    return dt

def convert_bi_dt(text):
    """
    convert string 'Sun Sep 26 2021 16:10:49 GMT+0000 (Coordinated Universal Time)' to Python date
    """
    text = text.replace('(Coordinated Universal Time)', '').strip()
    try:
        dt = datetime.strptime(text,"%a %b %d %Y %H:%M:%S GMT%z")
    except:
        dt = parser.parse(text)
    return dt

def convert_ft_dt(text):
    """
    convert string '1932-03-17T04:00:00+0000' to Python date
    """
    try:
        dt = datetime.strptime(text, "%Y-%m-%dT%H:%M:%S%z")
    except:
        dt = parser.parse(text)
    return dt

def strip_ft_bio(text):
    return text.replace("\n\t\t\t\t\t\t\t\t", '').replace("\n\t\t\t\t\t\t\t", '').strip()

def remove_mail_to(text):
    return text.replace("mailto:", '').strip()

def add_domain(text):
    domain_name ='https://www.ft.com'
    #domain_name = spider.domain
    return f"{domain_name}{text}".strip()

# def add_domain(text):
#     # Add a domain to a url extension
#     text = f"{allowed_domains+text}"

def parse_location(text):
    # parse location "in Ulm, Germany"
    # this simply remove "in ", you can further parse city, state, country, etc.
    return text[3:]

class TestItem(Item):
    Field(
        input_processor=Identity(),
        output_processor=Identity()
        )

class FT_ArticleItem(Item):
    published_date = Field(
        input_processor=MapCompose(convert_ft_dt),
        # TakeFirst return the first value not the whole list
        output_processor=TakeFirst()
        )
    headline = Field(
        input_processor=MapCompose(extract_headline),
        # TakeFirst return the first value not the whole list
        output_processor=Join()
        )
    # standfirst = Field(
    #     input_processor=MapCompose(extract_standfirst),
    #     output_processor=Join()
    #     )
    standfirst = Field(
        # Processed in pipeline due to limitations of Scrapy processors
        )
    article_summary = Field(
        input_processor=MapCompose(extract_headline),
        # TakeFirst return the first value not the whole list
        output_processor=Join()
        )
    image_caption = Field(
        input_processor=MapCompose(remove_articles),
        # TakeFirst return the first value not the whole list
        output_processor=Join()
        )
    article_content = Field(
        input_processor=MapCompose(remove_articles),
        # TakeFirst return the first value not the whole list
        output_processor=Join()
        )
    article_footnote = Field(
        input_processor=MapCompose(remove_articles),
        # TakeFirst return the first value not the whole list
        output_processor=Join()
        )
    article_link = Field(
        input_processor=MapCompose(add_domain),
        output_processor=TakeFirst()
        )
    # authors = Field(
    #     )
    authors = Field(
        input_processor=Identity()
        )
    tags = Field()
# # class ProfileField(scrapy.item.Field):

# class FT_AuthorItem(Item):
    # author_name = Field(
    #     input_processor=MapCompose(str.strip),
    #     output_processor=TakeFirst()
    #     )
    # author_position = Field(
    #     input_processor=MapCompose(str.strip),
    #     output_processor=Join()
    #     )
    # author_bio = Field(
    #     input_processor=MapCompose(strip_ft_bio),
    #     output_processor=Join()
    #     )
    # author_twitter = Field(
    #     input_processor=MapCompose(str.strip),
    #     output_processor=TakeFirst()
    #     )
    # author_email = Field(
    #     input_processor=MapCompose(remove_mail_to),
    #     output_processor=TakeFirst()
    #     )
    # author_birthday = Field(
    #     input_processor=MapCompose(convert_date),
    #     output_processor=TakeFirst()
    # )
    # author_bornlocation = Field(
    #     input_processor=MapCompose(parse_location),
    #     output_processor=TakeFirst()
    # )

# class AuthorItemLoader(ItemLoader):
#     default_input_processor=MapCompose(str.strip)
#     default_output_processor=TakeFirst()
#     default_item_class=FT_AuthorItem

class InsiderArticleItem(Item):
    published_date = Field(
        input_processor=MapCompose(convert_bi_dt),
        # TakeFirst return the first value not the whole list
        output_processor=TakeFirst()
        )
    headline = Field(
        input_processor=MapCompose(extract_headline),
        # TakeFirst return the first value not the whole list
        output_processor=Join()
        )
    # article_content = Field(
    #     input_processor=MapCompose(remove_articles),
    #     # TakeFirst return the first value not the whole list
    #     output_processor=TakeFirst()
    #     )
    # standfirst = Field(
    #     input_processor=MapCompose(extract_standfirst),
    #     output_processor=Join()
    #     )
    standfirst = Field(
        # Processed in pipeline due to limitations of Scrapy processors
        )
    article_link = Field(
        input_processor=MapCompose(add_domain),
        output_processor=TakeFirst()
        )
    author_names = Field(
        #input_processor=MapCompose(str.strip),
        #input_processor=Compose(str.strip),
        #output_processor=TakeFirst()
        )
    author_bio = Field(
        input_processor=MapCompose(strip_ft_bio),
        output_processor=TakeFirst()
        )
    author_twitter = Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
        )
    author_email = Field(
        input_processor=MapCompose(remove_mail_to),
        output_processor=TakeFirst()
        )
    tags = Field()

# class ArticleItem(Item):
#     published_date = Field(
#         input_processor=MapCompose(convert_date),
#         # TakeFirst return the first value not the whole list
#         output_processor=TakeFirst()
#         )
#     headline = Field(
#         input_processor=MapCompose(remove_space),
#         # TakeFirst return the first value not the whole list
#         output_processor=TakeFirst()
#         )
#     # article_content = Field(
#     #     input_processor=MapCompose(remove_articles),
#     #     # TakeFirst return the first value not the whole list
#     #     output_processor=TakeFirst()
#     #     )
#     standfirst = Field(
#         input_processor=MapCompose(remove_space),
#         # TakeFirst return the first value not the whole list
#         output_processor=TakeFirst()
#         )
#     # category = Field(
#     #     input_processor=MapCompose(remove_space),
#     #     # TakeFirst return the first value not the whole list
#     #     output_processor=TakeFirst()
#     #     )
#     author_names = Field(
#         input_processor=MapCompose(str.strip),
#         #output_processor=TakeFirst()
#         )
#     article_link = Field(
#         input_processor=MapCompose(str.strip),
#         output_processor=TakeFirst()
#         )
#     # author_birthday = Field(
#     #     input_processor=MapCompose(convert_date),
#     #     output_processor=TakeFirst()
#     # )
#     # author_bornlocation = Field(
#     #     input_processor=MapCompose(parse_location),
#     #     output_processor=TakeFirst()
#     # )
#     # author_bio = Field(
#     #     input_processor=MapCompose(str.strip),
#     #     output_processor=TakeFirst()
#     #     )
#     # tags = Field(
#     #     input_processor=MapCompose(remove_space),
#     #     # TakeFirst return the first value not the whole list
#     #     output_processor=TakeFirst()
#     #     )
#     tags = Field()

