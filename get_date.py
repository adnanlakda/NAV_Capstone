# TODO: Add doc string to describe module
# TODO: add comments throughout file to describe what it does

from newspaper import Article
import newspaper

def get_date(url):
    article = Article(url)
    article.download()
    article.parse()
    date = article.publish_date
    return str(date).split()[0]