# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

#import scrapy

from scrapy.item import Item, Field
#from scrapy.loader.processors import MapCompose, TakeFirst
from itemloaders.processors import MapCompose, TakeFirst, Compose
from datetime import datetime
from dateutil import parser
# dtt = parser.parse(dt)
# print (dtt)

def remove_articles(text):
    # strip the unicode articles
    text = text.strip(u'\u201c'u'\u201d')
    return text

def remove_space(text):
    # strip the unicode articles
    text = text.replace('  ', ' ')
    return text

def extract_headline(text):
    text = "".join(text)
    #text = text.strip(u'\u201c'u'\u201d')
    return text

def extract_standfirst(text):
    text =  "".join(text)
    text = text.replace('...“', '').replace('”...', '')
    #text = text.strip(u'\u201c'u'\u201d')
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


class FT_ArticleItem(Item):
    published_date = Field(
        input_processor=MapCompose(convert_ft_dt),
        # TakeFirst return the first value not the whole list
        output_processor=TakeFirst()
        )
    headline = Field(
        input_processor=MapCompose(extract_headline),
        # TakeFirst return the first value not the whole list
        output_processor=TakeFirst()
        )
    # article_content = Field(
    #     input_processor=MapCompose(remove_articles),
    #     # TakeFirst return the first value not the whole list
    #     output_processor=TakeFirst()
    #     )
    standfirst = Field(
        input_processor=MapCompose(extract_standfirst),
        # TakeFirst return the first value not the whole list
        output_processor=TakeFirst()
        )
    # category = Field(
    #     input_processor=MapCompose(remove_space),
    #     # TakeFirst return the first value not the whole list
    #     output_processor=TakeFirst()
    #     )
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
    # author_birthday = Field(
    #     input_processor=MapCompose(convert_date),
    #     output_processor=TakeFirst()
    # )
    # author_bornlocation = Field(
    #     input_processor=MapCompose(parse_location),
    #     output_processor=TakeFirst()
    # )
    # tags = Field(
    #     input_processor=MapCompose(remove_space),
    #     # TakeFirst return the first value not the whole list
    #     output_processor=TakeFirst()
    #     )
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