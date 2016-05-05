vectorizer_filename = "vectorizer.pkl"
vectorizer_kind = "tfidf"
vectorizer_args = {}

db_filename = "articles.db"
server = "0.0.0.0:5000"

query = dict(
        field="cs.LG",
        days_back=10,
        max_results=1000,
        keyword=None
)
