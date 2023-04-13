from json import JSONEncoder
import json
import os
from typing import List
import configparser
from os.path import join, dirname
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

class Article:
    """ Class meant to store the article data fetched from the Guardian API.
    """
    def __init__(self, web_title, section_name, web_url, publication_date, body_text):
        '''
        :param web_title: title of the article
        :param section_name: section of the article
        :param web_url: url of the article
        :param publication_date: date of publication of the article
        :param body_text: the text of the article
        '''
        self.web_title = web_title
        self.section_name = section_name
        self.web_url = web_url
        self.publication_date = publication_date
        self.body_text = body_text
class SummarizedArticle(Article):
    def __init__(self, web_title, section_name, web_url, publication_date, body_text, summary):
        super().__init__(web_title, section_name, web_url, publication_date, body_text)
        self.summary = summary

class ArticleEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

def clean_string(text: str) -> str:
    """ Function meant to clean a string object from ascii characters, newlines and tabs.

    Args:
        text (str): String object with ascii characters, newlines and tabs. 

    Returns:
        str: String object without ascii characters, newlines and tabs
    """
    text_encoded = text.encode("ascii", "ignore")
    text = text_encoded.decode()
    text = text.replace(r"\n", "")
    text = text.replace(r"\t", "")

    return text

def get_article() -> List[Article]:
    """ Function meant to retrieve the articles from the Guardian API.
    Function requires the API key to be stored in the .env file in the same directory as this file.
    Parameters are read from the config.ini.
    Function requests the articles from the Guardian API and returns a list of Article objects.

    Returns:
        List[Article]: List of Article objects with the articles from the Guardian API
    """
    # Path to .env file in the same directory as this file
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path=dotenv_path)
    # Get the API key from the environment variable
    api_key = os.environ.get("GUARDIAN_KEY")

    # read the config file
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "config.ini"))

    # get the parameters from the config file
    # if from_last_day is True, then the articles from the last day will be retrieved
    from_last_day= config["the_guardian"]["from_last_day"]
    # Check if the articles from the last day should be retrieved
    if from_last_day == "True":
        from_date = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d")
        to_date = datetime.now().strftime("%Y-%m-%d")
    else:
        from_date = config["the_guardian"]["from_date"]
        to_date = config["the_guardian"]["to_date"]

    order_by = config["the_guardian"]["order_by"]

    url_the_guardian_api = r'https://content.guardianapis.com/search'
    section = config["the_guardian"]["section"]
    # Page size 0 means that all articles from the given time period will be retrieved
    # Default page size in the Guardian API is 10
    page_size = config["the_guardian"]["page_size"]
    if page_size == "0":
        page_size = "200"
    url_modification = f'?from-date={from_date}&to-date={to_date}&order-by={order_by}&show-fields=bodyText&section={section}&page-size={page_size}&api-key={api_key}'
    # Request the articles from The Guardian API
    url = url_the_guardian_api + url_modification
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # get the content of the response
            content = response.json()
            # get list of articles
            articles = content["response"]["results"]
            # list of Article objects
            list_of_articles = []

            for article in articles:
                # get article details
                web_title = clean_string(article["webTitle"])
                section_name = clean_string(article["sectionName"])
                web_url = clean_string(article["webUrl"])
                publication_date = clean_string(article["webPublicationDate"])
                body_text = clean_string(article["fields"]["bodyText"])

                # create Article object
                article = Article(web_title, section_name, web_url, publication_date, body_text)
                list_of_articles.append(article)
            return list_of_articles
        else:
            print("Error: API request unsuccessful.")
            print(f"Status code: {response.json()['response']['message']}")
    except Exception as exception:
        print(exception)

def save_articles(articles: List[Article])-> None:
    """ Save the articles from a list of Article objects to a file in JSON format.
    Path to the folder where the articles will be saved is read from the config file.
    If the file already exists, a new file will be created with the corresponding number at 
    the end of the file name.

    Args:
        articles (List[Article]): List of Article objects meant to be saved to a file in JSON format
    """
    # Read path to folder where the articles will be saved from the config file
    config = configparser.ConfigParser()
    # config file is in the same directory as this file
    config.read(os.path.join(os.path.dirname(__file__), "config.ini"))
    path_to_folder = config["the_guardian"]["path_to_folder"]
    articles_section_name = articles[0].section_name.replace(" ", "-").lower()
    file_name = f"articles_{articles_section_name}_{articles[-1].publication_date[:10]}_{articles[0].publication_date[:10]}.json"
    # join the path to the folder with the file name
    absolute_path = os.path.join(path_to_folder, file_name)
    counter = 1
    while os.path.exists(absolute_path):
        print(f"File {file_name} already exists in {path_to_folder}.")
        new_file_name = f"{file_name.replace('.json','')}_{counter}.json"
        absolute_path = os.path.join(path_to_folder, new_file_name)
        counter += 1
    # Save the articles to a file
    with open(absolute_path, "w") as f:
        json.dump(articles, f, cls = ArticleEncoder, indent=4)

def load_articles(json_file_path:str, n_of_art:int=0) -> List[Article]:
    """ Loads the articles from a json file, which was saved by the save_articles function.

    Args:
        json_file_path (str): Path to the json file with the articles to be loaded.
        n_of_art (int, optional): Number of articles to be loaded. If number is
        set to 0, then all articles will be loaded. Defaults 0.

    Returns:
        List[Article]: List of Article objects loaded from the json file 
    """
    # Load the articles from a file from specified date
    with open(json_file_path, "r") as f:
        articles = json.load(f)
    # list of Article objects
    list_of_articles = []
    for article in articles:
        list_of_articles.append(Article(**article))
    # Return the specified number of articles
    # if n_of_art is 0, then all articles will be returned
    if n_of_art == 0:
        return list_of_articles
    return list_of_articles[:n_of_art]

if __name__ == "__main__":
    # Get the articles
    articles = get_article()
    # Save the articles to a file
    save_articles(articles)
