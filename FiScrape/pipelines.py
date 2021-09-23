# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem
from FiScrape.models import Article, Tag, db_connect, create_table, Topic, Source, Author #  create_output_table
from FiScrape.spiders.FiSpider import query
import logging

# class FiScrapePipeline:
#     def process_item(self, item, spider):
#         return item

class SaveArticlesPipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

# class SaveArticlesPipeline(object):
# #  To create a seperate table for each source
#     @classmethod
#     def from_crawler(cls, crawler):
#         return cls(crawler.spider.name)

#     def __init__(self, spider_name):
#         """
#         Initializes database connection and sessionmaker.
#         Creates deals table.
#         """
#         engine = db_connect()
#         create_output_table(engine, spider_name)


    def process_item(self, item, spider):
        """Save articles in the database
        This method is called for every item pipeline component
        """
        session = self.Session()
        article = Article()
        topic = Topic()
        source = Source()
        author = Author()
        tag = Tag()
        article.published_date = item["published_date"]
        article.headline = item["headline"]
        article.standfirst = item["standfirst"]
        article.article_link = item["article_link"]
        #article.article_content = item["article_content"]

        topic = Topic(name=query.capitalize())
        #topic.name = query.capitalize()
        # Check whether the topic already exists in the database
        exist_topic = session.query(Topic).filter_by(name = topic.name).first()
        if exist_topic is not None:  # the current topic exists
            topic = exist_topic
        article.topics.append(topic)
        #print("topic")

        #source = Source(name=spider.name)
        source.name = spider.name
        # Check whether the source already exists in the database
        exist_source = session.query(Source).filter_by(name = source.name).first()
        if exist_source is not None:  # the current author exists
            article.source = exist_source
        else:
            article.source = source

        #check whether the current article has authors or not
        if "author_names" in item:
            for author_name in item["author_names"]:
                author = Author(name=author_name)
                author.bio = item["author_bio"]
                author.twitter = item["author_twitter"]
                author.email = item["author_email"]
                #author.bias = item["author_bias"]
                # author.birthday = item["author_birthday"]
                # author.bornlocation = item["author_bornlocation"]
                # check whether the author exists
                exist_author = session.query(Author).filter_by(name = author.name).first()
                if exist_author is not None:  # the current author exists
                    author = exist_author
                article.authors.append(author)
                #print ("article_author")

        # check whether the current article has tags or not
        if "tags" in item:
            for tag_name in item["tags"]:
                tag = Tag(name=tag_name)
                # check whether the current tag already exists in the database
                exist_tag = session.query(Tag).filter_by(name = tag.name).first()
                if exist_tag is not None:  # the current tag exists
                    tag = exist_tag
                article.tags.append(tag)

        try:
            session.add(article)
            session.commit()

        except:
            session.rollback()
            #print ("rollback")
            raise

        finally:
            session.close()

        return item

class DuplicatesPipeline(object):

    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates tables.
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        logging.info("****DuplicatesPipeline: database connected****")

    def process_item(self, item, spider):
        session = self.Session()
        exist_article = session.query(Article).filter_by(article_link = item["article_link"]).first()
        session.close()
        if exist_article is not None:  # the current article exists
            topic_name = query.capitalize()
            if topic_name in exist_article.topics:
                raise DropItem("Duplicate item found: %s" % item["headline"])
            else:
                article = exist_article
                article.topics.append(topic_name)
                raise DropItem("Duplicate item found: %s" % item["headline"])
        else:
            return item


# class DuplicatesPipeline(object):

#     def __init__(self):
#         """
#         Initializes database connection and sessionmaker.
#         Creates tables.
#         """
#         engine = db_connect()
#         create_table(engine)
#         self.Session = sessionmaker(bind=engine)
#         logging.info("****DuplicatesPipeline: database connected****")

#     def process_item(self, item, spider):
#         session = self.Session()
#         exist_article = session.query(Article).filter_by(article_link = item["article_link"]).first()
#         session.close()
#         if exist_article is not None:  # the current article exists
#             raise DropItem("Duplicate item found: %s" % item["headline"])
#         else:
#             return item