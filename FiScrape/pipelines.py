# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem
from FiScrape.models import Article, Tag, db_connect, create_table, Topic, Source, Author, SnipBlob, Blob, SnipVader, Vader #  create_output_table
from FiScrape.spiders.FiSpider import query
from FiScrape.items import clean_text, extract_standfirst
import logging

# class FiScrapePipeline:
#     def process_item(self, item, spider):
#         return item

# class TestSpiderPipeline:
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
        snip_blob = SnipBlob()
        blob = Blob()
        snip_vader = SnipVader()
        vader = Vader()
        article.published_date = item["published_date"]
        article.headline = item["headline"]

        sf_list = []
        for sf_str in item["standfirst"]:
            sf_str = extract_standfirst(sf_str)
            sf_list.append(sf_str)
        sf = ' '.join(sf_list)
        sf = clean_text(sf)
        article.standfirst = sf
        #article.standfirst = item["standfirst"]
        article.article_link = item["article_link"]
        #article.article_content = item["article_content"]

        topic = Topic(name=query.capitalize())
        #topic.name = query.capitalize()
        # Check whether the topic already exists in the database
        exist_topic = session.query(Topic).filter_by(name = topic.name).first()
        if exist_topic is not None:  # the current topic exists
            topic = exist_topic
        article.topics.append(topic)

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
                if "author_bio" in item:
                    author.bio = item["author_bio"]
                if "author_twitter" in item:
                    author.twitter = item["author_twitter"]
                if "author_email" in item:
                    author.email = item["author_email"]
                if "author_bias" in item:
                    author.bias = item["author_bias"]
                if "author_birthday" in item:
                    author.birthday = item["author_birthday"]
                if "author_bornlocation" in item:
                    author.bornlocation = item["author_bornlocation"]
                # check whether the author exists
                exist_author = session.query(Author).filter_by(name = author.name).first()
                if exist_author is not None:  # the current author exists
                    author = exist_author
                article.authors.append(author)

        # check whether the current article has tags or not
        if "tags" in item:
            for tag_name in item["tags"]:
                tag = Tag(name=tag_name)
                # check whether the current tag already exists in the database
                exist_tag = session.query(Tag).filter_by(name = tag.name).first()
                if exist_tag is not None:  # the current tag exists
                    tag = exist_tag
                article.tags.append(tag)

        # Add sentiment scores
        head = article.headline 
        sf = article.standfirst
        # head = item["headline"]
        # sf = sf
        text = ' — ...'.join([head,sf])
        print ("TEXT:", text)

        snip_blob = SnipBlob()

        subjectivity_score = self.get_subjectivity(text)
        snip_blob.subjectivity = subjectivity_score
        polarity_score = self.get_polarity(text)
        snip_blob.polarity = polarity_score

        snip_vader = SnipVader()
        #SIA = 0
        SIA = self.get_SIA(text)
        compound = (SIA['compound'])
        neg = (SIA['neg'])
        neu = (SIA['neu'])
        pos = (SIA['pos'])
        snip_vader.compound = compound
        snip_vader.negative = neg
        snip_vader.neutral = neu
        snip_vader.positive = pos

        # article.snip_blob.append(snip_blob)
        # article.snip_vader.append(snip_vader)
        article.snip_blob = snip_blob
        article.snip_vader = snip_vader

        try:
            session.add(article)
            session.commit()

        except:
            session.rollback()
            raise

        finally:
            session.close()

        return item

    # Get the subjectivity
    def get_subjectivity(self, text):
        """
        Returns a subjectivity score between 0 and 1.
        0 is objective and 1 is subjective.
        """
        return TextBlob(text).sentiment.subjectivity

    # Get the polarity
    def get_polarity(self, text):
        """
        Returns a polarity score between -1 and 1.
        -1 is negative sentiment and 1 is positive sentiment.
        """
        return TextBlob(text).sentiment.polarity

    # Get the sentiment scores
    def get_SIA(self, text):
        sia = SentimentIntensityAnalyzer()
        sentiment =sia.polarity_scores(text)
        return sentiment

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
            # if topic_name in exist_article.topics:
            exist_topic = session.query(Topic).filter_by(name = topic_name).first()
            if exist_topic is not None:  # the current topic exists
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

import pandas as pd
import numpy as np
# pip install -U textblob
from textblob import TextBlob
import re
# pip install vaderSentiment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# # pip install -U scikit-learn
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score, classification_report
# from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
# from sklearn.preprocessing import RobustScaler

# class SentimentPipeline(object):

#     def __init__(self):
#         """
#         Initializes database connection and sessionmaker.
#         Creates tables.
#         """
#         engine = db_connect()
#         create_table(engine)
#         self.Session = sessionmaker(bind=engine)
#         logging.info("****SentimentPipeline: database connected****")

#     def get_sentiment(self, item, spider):
#         """
#         Calculates and stores sentiment scores for the snippet (headline & standfirst), and the article body, if it was scraped.
#         """
#         session = self.Session()
#         exist_article = session.query(Article).filter_by(article_link = item["article_link"]).first()
#         session.close()
#         if exist_article is not None:  # the current article exists
#             article = exist_article
#             head = article.headline
#             sf = article.standfirst
#             text = ' — ...'.join([head,sf])

#             snip_blob = SnipBlob(name=article.article_link)

#             subjectivity_score = self.get_subjectivity(text)
#             snip_blob.subjectivity = subjectivity_score
#             polarity_score = self.get_polarity(text)
#             snip_blob.polarity = polarity_score

#             snip_vader = SnipVader(name=article.article_link)
#             SIA = 0
#             SIA = self.get_SIA(text)
#             compound = (SIA['compound'])
#             neg = (SIA['neg'])
#             neu = (SIA['neu'])
#             pos = (SIA['pos'])
#             snip_vader.compound = compound
#             snip_vader.negative = neg
#             snip_vader.neutral = neu
#             snip_vader.negative = neg
            
#         try:
#             article.snip_blob.append(snip_blob)
#             article.snip_vader.append(snip_vader)
#             session.update(article)
#             session.commit()

#         except:
#             session.rollback()
#             raise

#         finally:
#             session.close()

#     # Get the subjectivity
#     def get_subjectivity(self, text):
#         """
#         Returns a subjectivity score between 0 and 1.
#         0 is objective and 1 is subjective.
#         """
#         return TextBlob(text).sentiment.subjectivity

#     # Get the polarity
#     def get_polarity(self, text):
#         """
#         Returns a polarity score between -1 and 1.
#         -1 is negative sentiment and 1 is positive sentiment.
#         """
#         return TextBlob(text).sentiment.polarity

#     # Get the sentiment scores
#     def get_SIA(text):
#         sia = SentimentIntensityAnalyzer()
#         sentiment =sia.polarity_scores(text)
#         return sentiment