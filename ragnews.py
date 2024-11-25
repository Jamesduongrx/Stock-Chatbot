#!/bin/python3

'''
Run an interactive QA session with the news articles using the Groq LLM API and retrieval augmented generation (RAG).

New articles can be added to the database with the --add_url parameter,
and the path to the database can be changed with the --db parameter.
'''

from urllib.parse import urlparse
import datetime
import logging
import re
import sqlite3
import groq
from groq import Groq
import os
import requests
from bs4 import BeautifulSoup
import finnhub

################################################################################
# LLM functions
################################################################################

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def run_llm(system, user, model='llama3-8b-8192', seed=None):
    '''
    This is a helper function for all the uses of LLMs in this file.
    '''
    chat_completion = client.chat.completions.create(
        messages=[
            {
                'role': 'system',
                'content': system,
            },
            {
                "role": "user",
                "content": user,
            }
        ],
        model=model,
        seed=seed,
    )
    return chat_completion.choices[0].message.content

def summarize_text(text, seed=None):
    system = 'Summarize the input text below. Limit the summary to 1 paragraph. Use an advanced reading level similar to the input text, and ensure that all people, places, and other proper names and dates are included in the summary. The summary should be in English. Only include the summary.'
    return run_llm(system, text, seed=seed)

def extract_company(keywords, seed=None):
    system = 'Identify what company the user is interested in learning more about. Only return that company in your output. If the user does not reference any company, return nothing. If the user '
    return run_llm(system, keywords, seed=seed)

def extract_date(keywords, seed=None):
    system = '''Identify what date range the user is interested in. 
    This will be used to search for articles relevant to the date range the user mentions. 
    Only output a list with two string variables, the first being the start date in YYYY-MM-DD format and the second being the end date also in YYYY-MM-DD format. 
    If the user does not reference any specific dates, output the list with the start date being one month in before today YYYY-MM-DD format and the end date being today in YYYY-MM-DD format.'''
    return run_llm(system, keywords, seed=seed)

def extract_keywords(text, seed=None):
    '''
    This is a helper function for RAG.
    Given an input text, this function extracts the keywords that will be used to perform the search for articles that will be used in RAG.

    >>> extract_keywords('Who is the current democratic presidential nominee?', seed=0)
    'Democratic nominee 2024 Biden'
    >>> extract_keywords('What are some policy differences between Harris and Trump?', seed=0)
    'Harris Trump policy differences'
    '''

    system = """
    Do not answer the question. 
    Only provide a string containing 5-10 of the top keywords relevant to the topic that would benefit a search for articles online relating to the question. 
    Separate each keyword with a space. 
    Prioritize names, actions, and dates in the string of keywords.
    Follow these rules:
    1. Escape or format any special characters (like single quotes, apostrophes, etc.) that could cause problems in a query.
    2. Return the keywords as a single string, formatted such that numbers and special characters do not break any query syntax.
    For example, if the question is: 'Does Bloomberg recommend buying for Apple?', an acceptable output would be: Bloomberg apple recommendation.
    Another example, if the question is: 'What are some of the challenges Tesla is currently facing?' , an acceptable output would be: Tesla recent challenges.
    """
    keywords = run_llm(system, text, seed=seed)
    return keywords

finnhub_client = finnhub.Client(
    api_key=os.environ.get("FINN_API_KEY"),
    )

def get_symbol(keywords):
    return finnhub_client.symbol_lookup(keywords)

def get_most_popular_symbol(keywords):
    company = extract_company(keywords)
    if company is None:
        return "No company mentioned by user"
    else:
        search_results = get_symbol(company)
        if search_results['count'] == 0:
            return "No results found."
        # Filter for 'Common Stock' or other criteria for popularity
        common_stocks = [
            item for item in search_results['result'] 
            if item['type'] == 'Common Stock'
        ]
        # If there are common stocks, return the first one
        if common_stocks:
            return common_stocks[0]['displaySymbol']
        # Fallback: return the first result if no common stocks are found
        return search_results['result'][0]['displaySymbol']

def get_quote(ticker):
    return finnhub_client.quote(ticker)
    
def get_news(ticker, keywords):
    dates = extract_date(keywords)
    news_results = finnhub_client.company_news(ticker, _from=dates[0], to=dates[1])
    if news_results is None:
        return "No news results found"
    articles = []
    for row in news_results:
        articles.append({
            'headline': news_results['headline'],
            'sourcd': news_results['source'],
            'summary': news_results['summary'],
            'url': news_results['url']
                })
    return articles



################################################################################
# helper functions
################################################################################

def _logsql(sql):
    rex = re.compile(r'\W+')
    sql_dewhite = rex.sub(' ', sql)
    logging.debug(f'SQL: {sql_dewhite}')


def _catch_errors(func):
    '''
    This function is intended to be used as a decorator.
    It traps whatever errors the input function raises and logs the errors.
    We use this decorator on the add_urls method below to ensure that a webcrawl continues even if there are errors.
    '''
    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logging.error(str(e))
    return inner_function


################################################################################
# rag
################################################################################

def rag(text, db):
    '''
    This function uses retrieval augmented generation (RAG) to generate an LLM response to the input text.
    The db argument should be an instance of the `ArticleDB` class that contains the relevant documents to use.
    '''
    keywords = extract_keywords(text)
    sanitized_keywords = keywords.replace("'", "''")
    print(f"Keywords: {keywords}")  # Debug the keywords
    articles = db.find_articles(sanitized_keywords, limit=10, timebias_alpha=1)
    print(f"Retrieved {len(articles)} articles")
    
    system = """You are a professional news analyst tasked with answering questions based solely on the provided articles. 
    Do not take into account any knowledge outside of the articles in your answer.
    Your responses should be concise, accurate, and directly address the question. 
    You must summarize key information from the articles clearly in at most three complete sentences. 
    Do not add any extra details, opinions, or unnecessary explanations. 
    You are not allowed to talk about or mention the source of your information or articles in your answer.
    Present the information as if you have done the research yourself.
    Stop responding once you have provided the necessary answer. \n\n"""

    string_articles = ""
    for article in articles:
        if article['text']:
            string_articles += (f"Title: {article['title']}\nContent: {article['text'][:2000]}\n\n")
        else:
            logging.warning(f"Article with title '{article['title']}' has no text content.")
    if not string_articles:
        return "No relevant articles with text found for the query."
    string_articles = summarize_text(string_articles)
    system += string_articles
    system += f"User query: {text}"

    return run_llm(system, text)


################################################################################
# ArticleDB class (with metahtml replacement using BeautifulSoup)
################################################################################

class ArticleDB:
    '''
    This class represents a database of news articles.
    It is backed by sqlite3 and designed to have no external dependencies.

    >>> db = ArticleDB()
    >>> len(db)
    0
    >>> db.add_url(ArticleDB._TESTURLS[0])
    >>> len(db)
    1

    >>> articles = db.find_articles('Economía')
    >>> articles[0]['title']
    'La creación de empleo defrauda en Estados Unidos en agosto y aviva el temor a una recesión | Economía | EL PAÍS'
    >>> list(articles[0].keys())
    ['rowid', 'rank', 'title', 'publish_date', 'hostname', 'url', 'staleness', 'timebias', 'en_summary', 'text']
    '''

    _TESTURLS = [
        'https://elpais.com/economia/2024-09-06/la-creacion-de-empleo-defrauda-en-estados-unidos-en-agosto-y-aviva-el-fantasma-de-la-recesion.html',
        'https://www.cnn.com/2024/09/06/politics/american-push-israel-hamas-deal-analysis/index.html',
    ]

    def __init__(self, filename=':memory:'):
        self.db = sqlite3.connect(filename)
        self.db.row_factory = sqlite3.Row
        self.logger = logging
        self._create_schema()

    def _create_schema(self):
        '''
        Create the DB schema if it doesn't already exist.

        >>> db = ArticleDB()
        >>> db._create_schema()
        >>> db._create_schema()  # Ensure no errors when schema already exists
        '''
        try:
            sql = '''
            CREATE VIRTUAL TABLE articles
            USING FTS5 (
                title,
                text,
                hostname,
                url,
                publish_date,
                crawl_date,
                lang,
                en_translation,
                en_summary
                );
            '''
            self.db.execute(sql)
            self.db.commit()
        except sqlite3.OperationalError:
            self.logger.debug('CREATE TABLE failed')

    def find_articles(self, query, limit=10, timebias_alpha=1):
        '''
        Return a list of articles in the database that match the specified query.
        '''
        cursor = self.db.cursor()

        sanitized_query = query.replace("'", "''")  # Escapes single quotes

        sql = '''
        SELECT rowid, title, text, publish_date, hostname, url, bm25(articles) AS rank        FROM articles
        WHERE articles MATCH ?
        ORDER BY rank
        LIMIT ?;
        '''
        
        articles = []
        try:
            cursor.execute(sql, (sanitized_query, limit))
            rows = cursor.fetchall()
            for row in rows:
                articles.append({
                    'rowid': row['rowid'],
                    'rank': row['rank'],
                    'title': row['title'],
                    'publish_date': row['publish_date'],
                    'hostname': row['hostname'],
                    'url': row['url'],
                    'staleness': None,  # Placeholder for staleness
                    'timebias': timebias_alpha,  # Placeholder for timebias
                    'en_summary': None,  # Placeholder for en_summary
                    'text': row['text']
                })
        except sqlite3.OperationalError as e:
            print(f"SQLite error: {e}")
        return articles

    @_catch_errors
    def add_url(self, url, recursive_depth=0, allow_dupes=False):
        '''
        Download the url, extract various metainformation, and add the metainformation into the db.
        '''
        logging.info(f'add_url {url}')

        if not allow_dupes:
            cursor = self.db.cursor()
            sql = 'SELECT count(*) FROM articles WHERE url=?;'
            _logsql(sql)
            cursor.execute(sql, [url])
            row = cursor.fetchone()
            if row[0] > 0:
                logging.debug('Duplicate detected, skipping!')
                return

        logging.debug(f'downloading url')
        try:
            response = requests.get(url)
        except requests.exceptions.MissingSchema:
            url = 'https://' + url
            response = requests.get(url)
        
        parsed_uri = urlparse(url)
        hostname = parsed_uri.netloc

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extracting metadata manually
        title = soup.find('title').text if soup.find('title') else None
        content = soup.find('body').get_text() if soup.find('body') else None

        # Example of extracting publish date (this depends on the website's structure)
        publish_date = soup.find('meta', {'name': 'publish_date'})
        if publish_date:
            publish_date = publish_date['content']

        # Example of extracting language (again, depends on the HTML structure)
        language = soup.find('html')['lang'] if soup.find('html') and 'lang' in soup.find('html').attrs else None

        # Construct the simplified metadata dictionary manually
        info = {
            'title': title,
            'content': {'text': content},
            'timestamp.published': {'lo': publish_date},
            'language': language,
            'type': 'article' if content and len(content) > 100 else 'other'
        }

        if info['type'] != 'article' or len(info['content']['text']) < 100:
            logging.debug('Not an article... skipping')
            en_translation = None
            en_summary = None
            info['title'] = None
            info['content'] = {'text': None}
            info['timestamp.published'] = {'lo': None}
            info['language'] = None
        else:
            logging.debug('Summarizing')
            if not info['language'].startswith('en'):
                en_translation = translate_text(info['content']['text'])
            else:
                en_translation = None
            en_summary = summarize_text(info['content']['text'])

        logging.debug('Inserting into database')
        sql = '''
        INSERT INTO articles(title, text, hostname, url, publish_date, crawl_date, lang, en_translation, en_summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        '''
        _logsql(sql)
        cursor = self.db.cursor()
        cursor.execute(sql, [
            info['title'],
            info['content']['text'],
            hostname,
            url,
            info['timestamp.published']['lo'],
            datetime.datetime.now().isoformat(),
            info['language'],
            en_translation,
            en_summary,
        ])
        self.db.commit()

        logging.debug('Recursively adding more links')
        if recursive_depth > 0:
            for link in soup.find_all('a', href=True):
                url2 = link['href']
                parsed_uri2 = urlparse(url2)
                hostname2 = parsed_uri2.netloc
                if hostname in hostname2 or hostname2 in hostname:
                    self.add_url(url2, recursive_depth-1)

    def __len__(self):
        '''
        Return the number of articles in the database.
        '''
        sql = '''
        SELECT count(*)
        FROM articles
        WHERE text IS NOT NULL;
        '''
        _logsql(sql)
        cursor = self.db.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        return row[0]

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--loglevel', default='warning')
    parser.add_argument('--db', default='ragnews.db')
    parser.add_argument('--recursive_depth', default=0, type=int)
    parser.add_argument('--add_url', help='If this parameter is added, then the program will not provide an interactive QA session with the database. Instead, the provided URL will be downloaded and added to the database.')
    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=args.loglevel.upper(),
    )

    db = ArticleDB(args.db)

    if args.add_url:
        db.add_url(args.add_url, recursive_depth=args.recursive_depth, allow_dupes=True)

    else:
        import readline
        while True:
            text = input('ragnews> ')
            if len(text.strip()) > 0:
                output = rag(text, db)
                print(output)