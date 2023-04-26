# TODO: Add doc string to describe module
# TODO: add comments throughout file to describe what it does

from newspaper import Article
import newspaper

def get_date(url):
    """
        Extracts the publication date from a given news article URL.

        Parameters:
         url (str): The URL of the news article.

        Returns:
        str: The publication date of the news article in YYYY-MM-DD format.
    """

    try:
        article = Article(url)
        article.download()
        article.parse()
        date = article.publish_date
        return str(date).split()[0]
    except: 
        return '2023-00-00'
    