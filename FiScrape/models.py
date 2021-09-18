from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text)
from scrapy.utils.project import get_project_settings

Base = declarative_base()

CONNECTION_STRING = 'sqlite:///FiScrape.db'

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    # return create_engine(get_project_settings().get("CONNECTION_STRING"))
    return create_engine(CONNECTION_STRING)


def create_table(engine):
    Base.metadata.create_all(engine)

# Association Table for Many-to-Many relationship between Article and Tag
# https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html#many-to-many
article_tag = Table('article_tag', Base.metadata,
    Column('article_id', Integer, ForeignKey('article.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)


class Article(Base):
    __tablename__ = "article"

    id = Column(Integer, primary_key=True)
    article_content = Column('article_content', Text())
    author_id = Column(Integer, ForeignKey('author.id'))  # Many articles to one author
    tags = relationship('Tag', secondary='article_tag',
        lazy='dynamic', backref="article")  # M-to-M for article and tag


class Author(Base):
    __tablename__ = "author"

    id = Column(Integer, primary_key=True)
    name = Column('name', String(50), unique=True)
    birthday = Column('birthday', DateTime)
    bornlocation = Column('bornlocation', String(150))
    bio = Column('bio', Text())
    articles = relationship('Article', backref='author')  # One author to many Articles


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True)
    name = Column('name', String(30), unique=True)
    articles = relationship('Article', secondary='article_tag',
        lazy='dynamic', backref="tag")  # M-to-M for article and tag