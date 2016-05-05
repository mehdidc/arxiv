import pickle
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.pipeline import make_pipeline
from lda import LDA


def build_tfidf_from_documents(documents, **kw):
    vectorizer = TfidfVectorizer(min_df=1, stop_words='english', ngram_range=(1, 2))
    vectorizer.fit(documents)
    return vectorizer


def build_lda_from_documents(documents, n_topics=20, **kw):
    fe = make_pipeline(
        CountVectorizer(min_df=1),
        LDA(n_topics=n_topics, n_iter=100)
    )
    fe.fit(documents)
    return fe

builder = {
    "tfidf": build_tfidf_from_documents,
    "lda": build_lda_from_documents
}


def save(vectorizer, filename):
    with open(filename, "w") as fd:
        pickle.dump(vectorizer, fd)


def load(filename):
    with open(filename, "r") as fd:
        vectorizer = pickle.load(fd)
    return vectorizer
