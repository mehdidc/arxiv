from invoke import task
from feed import get_new_entries
from helpers import replace_config

import config


@task
def create_db(config_module=None):
    from db import build_instance
    replace_config(config_module)
    db = build_instance()
    db.create()
    db.finish()


@task
def add_new_articles(config_module=None):
    from db import (build_instance, build_article_from_entry,
                    build_authors_from_entry)
    from arxiv import build_feed_url
    replace_config(config_module)
    url = build_feed_url(**config.query)
    print(url)
    entries = get_new_entries(url)
    articles = map(build_article_from_entry, entries)
    authors_per_article = map(build_authors_from_entry, entries)
    db = build_instance()
    db.push_articles_and_authors(articles, authors_per_article)
    db.finish()


@task
def rebuild_vectorizer(config_module=None):
    import vectorizer
    from db import build_instance, article_to_document
    replace_config(config_module)
    db = build_instance()
    articles = db.get_articles()
    db.finish()
    documents = map(article_to_document, articles)
    builder = vectorizer.builder[config.vectorizer_kind]
    vect = builder(documents, **config.vectorizer_args)
    vectorizer.save(vect, config.vectorizer_filename)
