from datetime import date, timedelta
from collections import OrderedDict

feed_url_template = "http://export.arxiv.org/api/query?{content}"
submitted_date_template = "[{begin}000000+TO+{end}000000]"


def build_feed_url(field="cs.LG", max_results=500, days_back=10, keyword=None):
    if days_back is not None:
        today = format_date(date.today())
        yesterday = format_date(date.today() - timedelta(days_back))
    query = OrderedDict()
    query["start"] = 0
    query["max_results"] = max_results
    search_query = dict()
    query["search_query"] = search_query
    if field is not None:
        search_query["cat"] = field
    if days_back is not None:
        search_query["submittedDate"] = dict(begin=yesterday, end=today)
    if keyword is not None:
        search_query["all"] = keyword
    url = build_feed_url_from_dict(query)
    return url


def build_feed_url_from_dict(query):
    content = OrderedDict()
    content.update(query)

    search_query = content["search_query"]
    if "submittedDate" in search_query:
        search_query["submittedDate"] = (
            submitted_date_template.format(**search_query["submittedDate"]))

    search_query = ["{}:{}".format(name, preprocess_(val))
                    for name, val in search_query.items()]
    search_query = "+AND+".join(search_query)
    content["search_query"] = search_query
    content = ["{}={}".format(name, preprocess_(val))
               for name, val in content.items()]
    content = "&".join(content)
    return feed_url_template.format(content=content)


def preprocess_(s):
    return s.replace(" ", "+") if type(s) == str else s


def format_date(d):
    return "{year:04d}{month:02d}{day:02d}".format(year=d.year, month=d.month, day=d.day)

def id_from_string(s):
    return s

date_format = "%Y-%m-%dT%H:%M:%SZ"
