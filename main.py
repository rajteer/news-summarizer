import article
import extractive_sum
import send_email
import datetime
from typing import List
import configparser
import os

def construct_email_body(articles: List[article.Article]) -> str:
    """ Function is meant to construct the email body from the given articles.
        It will get the number of articles to be summarized from the config file.
        It will also get the summary of each article using the extractive summarization
        algorithm, which is implemented in the extractive_sum module. The summary
        will be added to the email body. Email text is written in HTML format to allow
        elegant formatting of the email. 

    Args:
        articles (List[article.Article]): list of articles to be summarized and added to the email 
        body. Individual articles are of type article.Article, which is implemented in the article 
        module.

    Returns:
        str: email body written in HTML format.
    """
    # get the number of articles to be summarized from the config file
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "config.ini"))
    try:
        n_of_articles = int(config["recipients"]["n_of_articles"])
    except ValueError:
        print("Number of articles not set")
        raise ValueError("Number of articles not set")
    # if the number of articles to be summarized is greater than the number of articles
    # available, set the number of articles to be summarized to the number of articles available
    if n_of_articles > len(articles):
        n_of_articles = len(articles)
    articles_text = ""
    for fetched_article in articles[:n_of_articles]:
        article_header = fetched_article.web_title
        article_text = extractive_sum.get_summary(fetched_article.body_text)
        article_pub_date = fetched_article.publication_date
        articles_text += f"""
        <h2>{article_header}</h2>
        <i>{article_pub_date}</i>
        <p>{article_text}</p>"""
    date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    email_body = f"""<!DOCTYPE html>
    <html>
    <head></head>
    <body>
        <h1>Summary from {date}.</h1>
        {articles_text}
        </body>
        </html>"""
    return email_body

def main():
    """ Main function of the summarizer module. It will get the articles from the article module, 
        construct the email body using the construct_email_body function, in which the extractive
        summarization algorithm is implemented. It will then send the email using the send_email
        module.
    """
    articles = article.get_article()
    email_body = construct_email_body(articles)
    email_title = f"Summary from {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
    send_email.send_email(email_body, email_title)

if __name__ == "__main__":
    main()
