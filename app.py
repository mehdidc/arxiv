from collections import OrderedDict

from flask import Flask, render_template, request, url_for, redirect
from db import build_instance, article_to_document

import vectorizer
import config

from numpy import dot
from scipy.sparse import issparse

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.pipeline import make_pipeline

from helpers import to_multiline, replace_config


from flask.ext.cache import Cache

app = Flask(__name__)

cache = Cache(app, config={'CACHE_TYPE': 'simple'})


app.debug = True
db = None
timeout = 3600


@app.route('/')
def index():
    return redirect(url_for('articles_list'))


def make_cache_key(*args, **kwargs):
    like = request.args.get("like")
    like = "" if like is None else like
    return request.path + like


@app.route('/articles', methods=["GET"])
@cache.cached(timeout=timeout)
def articles_list():
    articles = list(db.get_articles_sorted_by_date())
    like = request.args.get("like")
    if like:
        like = int(like)
        vect = vectorizer.load(config.vectorizer_filename)
        documents = map(article_to_document, articles)
        vects = vect.transform(documents)
        if issparse(vects):
            vects = vects.toarray()
        article_index = map(lambda article: article.id, articles).index(like)
        article_vect = vects[article_index]
        app.logger.info(type(vects[0]), type(article_vect))
        sim = [dot(v, article_vect) for v in vects]
        order = reversed(sorted(range(len(articles)),
                                key=lambda idx: sim[idx]))
        articles = [articles[pos] for pos in order]

    return render_template("show_entries.html", entries=articles)

articles_list.make_cache_key = make_cache_key


@app.route('/embedding')
@cache.cached(timeout=timeout)
def embedding():
    from bokeh.plotting import figure
    from bokeh.resources import INLINE
    from bokeh.models import HoverTool, ColumnDataSource
    from bokeh.embed import components
    # from sklearn.manifold import Isomap

    articles = list(db.get_articles())
    vect = vectorizer.load(config.vectorizer_filename)
    documents = map(article_to_document, articles)
    vects = vect.transform(documents)
    if issparse(vects):
        vects = vects.toarray()
    
    #E = PCA(n_components=2)
    E = make_pipeline(
        PCA(n_components=50),
        TSNE(n_components=2, perplexity=30, early_exaggeration=4, verbose=1)
    )
    embed = E.fit_transform(vects)
    _, pca = E.steps[0]
    print(pca.explained_variance_ratio_)
    titles = map(lambda article: article.title, articles)
    titles = map(lambda title: to_multiline(title, max_line_length=30), titles)
    titles = map(lambda title: "".join(title), titles)

    links = [article.link for article in articles]

    authors = map(lambda article: article.authors, articles)
    authors = map(lambda author: [a.name for a in author], authors)
    authors = map(lambda author: ",".join(author), authors)
    authors = map(lambda author: to_multiline(author, max_line_length=30),
                  authors)
    authors = map(lambda author: "".join(author)[0:40]+"[...]", authors)

    ds = ColumnDataSource(
        dict(x=embed[:, 0],
             y=embed[:, 1],
             title=titles,
             link=links,
             author=authors)
    )

    tools = "resize, hover, save, pan,wheel_zoom,box_zoom,reset,resize"
    fig = figure(title="paper embedding", tools=tools,
                 width=1400, height=800)
    fig.scatter("x", "y", source=ds, size=5, marker='cross')
    hover = fig.select(dict(type=HoverTool))
    hover.tooltips = OrderedDict([
        ("title", "@title"),
        ("author", "@author"),
        ("link", "@link"),
    ])

    app.logger.info(INLINE.__dict__.keys())
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = components(fig, INLINE)

    html = render_template(
        'figure.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
    )
    return html


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.finish()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='WebServer')
    parser.add_argument("--config-module",
                        type=str, help="config filename",
                        default="config")
    parser.add_argument("--host",
                        type=str,
                        default="0.0.0.0")
    parser.add_argument("--port",
                        type=int,
                        default=5000)
    args = parser.parse_args()
    replace_config(args.config_module)
    db = build_instance()
    app.run(host=args.host, port=args.port)
