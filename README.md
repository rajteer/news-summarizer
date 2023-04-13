# Automated news article summarizer
A python script that scrapes the news articles, summarizes them and sends them to the user's defined email address. 

## Introduction <a name="introduction"></a>
The main goal of this project was to create an automated news fetcher and summarizer. The idea was to create a script that would fetch the news articles from the web and summarize them. The script is written in Python and uses the following libraries:
* `requests` - to fetch the news articles from theguardian.com API,
* `beautifulsoup4` - to parse the html code of the news articles,
* `nltk` - to tokenize the text,
* `numpy` - to create the word vectors,
* `pandas` - to create the data frame,
* `networkx` - to create the graph,
* `smtplib` - to send the email message,
* `keyring` - to save the user's password in the windows credential manager.
## Usage 

Project contains four .py files:
* `main.py` - main file that calls all the functions and runs the script,
* `news.py` - contains functions that fetch the news articles from theguardian.com API and save it in .json format,
* `summarizer.py` - contains functions that summarize the news articles by using the extractive TextRank algorithm which is based on the PageRank algorithm,
* `send_mail.py` - contains functions that send the summarized news articles to the user's email address, it also contains the function to save securlly the user's password in the windows credential manager.

To run the script, you also need to have the following files in the same directory:
* `glove.6B.100d.txt` - a pre-trained word embedding model that is used to create the word vectors,
* `config.ini` - a configuration file that contains for example the recipient's email address, information about the email server, etc.

In .env file you need to add sender's email address and API key for theguardian.com API.

Feel free to use the script and modify it to your needs. If you find any bugs or have any suggestions, please let me know.