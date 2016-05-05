import feedparser


def get_new_entries(feed_url):
    feed = feedparser.parse(feed_url)
    entries = feed.entries
    return entries
