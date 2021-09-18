# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

from scrapy.item import Item, Field
from scrapy.loader.processors import MapCompose, TakeFirst
# from itemloaders.processors import MapCompose, TakeFirst
from datetime import datetime


def remove_articles(text):
    # strip the unicode articles
    text = text.strip(u'\u201c'u'\u201d')
    return text

def remove_space(text):
    # strip the unicode articles
    text = text.replace('  ', ' ')
    return text

def convert_date(text):
    # convert string March 14, 1879 to Python date
    return datetime.strptime(text, '%B %d, %Y')

# def add_domain(text):
#     # Add a domain to a url suffix
#     text = f"{allowed_domains+text}"


def parse_location(text):
    # parse location "in Ulm, Germany"
    # this simply remove "in ", you can further parse city, state, country, etc.
    return text[3:]


class ArticleItem(Item):
    published_date = Field(
        input_processor=MapCompose(convert_date),
        # TakeFirst return the first value not the whole list
        output_processor=TakeFirst()
        )
    headline = Field(
        input_processor=MapCompose(remove_space),
        # TakeFirst return the first value not the whole list
        output_processor=TakeFirst()
        )
    # article_content = Field(
    #     input_processor=MapCompose(remove_articles),
    #     # TakeFirst return the first value not the whole list
    #     output_processor=TakeFirst()
    #     )
    standfirst = Field(
        input_processor=MapCompose(remove_space),
        # TakeFirst return the first value not the whole list
        output_processor=TakeFirst()
        )
    # category = Field(
    #     input_processor=MapCompose(remove_space),
    #     # TakeFirst return the first value not the whole list
    #     output_processor=TakeFirst()
    #     )
    author_name = Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
        )
    article_link = Field(
        input_processor=MapCompose(str.strip),
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
    # author_bio = Field(
    #     input_processor=MapCompose(str.strip),
    #     output_processor=TakeFirst()
    #     )
    # tags = Field(
    #     input_processor=MapCompose(remove_space),
    #     # TakeFirst return the first value not the whole list
    #     output_processor=TakeFirst()
    #     )
    tags = Field()