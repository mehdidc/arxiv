from datetime import datetime

from sqlalchemy import (create_engine, Column, Integer, String, 
        DateTime, ForeignKey, UniqueConstraint, Table)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy import desc

import config

Base = declarative_base()

class Article(Base):
    __tablename__ = "Article"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    title = Column(String)
    summary = Column(String)
    link = Column(String)
    authors = Column(String)
    datetime = Column(DateTime)

    authors = relationship("Author", secondary='ArticleAuthor')

    def __repr__(self):
        return u"{} by {}".format(self.title, self.authors)

    def to_document(self):
        return u"{}\n{}".format(self.title, self.summary)

    def add_authors(self, authors):
        for author in authors:
            article_author = ArticleAuthor()

class Author(Base):

    __tablename__ = "Author"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    article_id = Column(Integer, ForeignKey(Article.id))

    def __repr__(self):
        self.name.encode("utf-8")
        return self.name

ArticleAuthor = Table('ArticleAuthor', Base.metadata,
    Column('Article.id', Integer, ForeignKey('Author.id')),
    Column('Author.id', Integer, ForeignKey('Article.id'))
)


article_to_document = Article.to_document

class Instance(object):

    def __init__(self, engine):
        self.engine = engine
        self.session = scoped_session(sessionmaker(bind=engine))

    def create(self):
        Base.metadata.create_all(self.engine)

    def push_articles(self, articles):
        for article in articles:
            self.session.add(article)
        self.session.commit()

    def push_articles_and_authors(self, articles, authors_per_article):
        for article, authors in zip(articles, authors_per_article):

            if not instance_exists(article, self.session, field="name"):
                self.session.add(article)
            for author in authors:
                author = replace_if_exists(author, self.session, field="name")
                article.authors.append(author)
        self.session.commit()

    def push_authors(self, authors):
        for author in authors:
            self.session.add(author)
        self.session.commit()

    def get_articles(self):
        return self.session.query(Article)
    
    def get_articles_sorted_by_date(self):
        return self.get_articles().order_by(desc(Article.datetime))

    def finish(self):
        self.session.remove()

def instance_exists(instance, session, field="id"):
    params = {field: getattr(instance, field)}
    return session.query(instance.__class__).filter_by(**params).first()


def replace_if_exists(instance, session, field="id"):
    params = {field: getattr(instance, field)}
    instance_ = session.query(instance.__class__).filter_by(**params).first()
    return instance_ if instance_ else instance

def build_instance(filename=None):
    if filename is None:
        filename = config.db_filename
    engine = create_engine('sqlite:///{}'.format(filename), echo=True)
    return Instance(engine)

import arxiv
def build_article_from_entry(entry):
    article = Article()
    article.name = entry.id
    article.title = entry.title
    article.summary = entry.summary_detail.value
    article.link = entry.link
    article.datetime = datetime.strptime(entry.published,
                                         arxiv.date_format)
    return article

def build_authors_from_entry(entry):
    authors = []
    for author_ in entry.authors:
        author = Author()
        author.name = author_.name
        authors.append(author)
    return authors
