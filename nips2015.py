vectorizer_filename = "vectorizer-nips2015.pkl"
vectorizer_kind = "tfidf"
vectorizer_args = {}


db_filename = "articles-nips2015.db"

query = dict(
        max_results=1000,
        keyword="NIPS",
        days_back=None,
        field="cs.LG",
)
