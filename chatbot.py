#!/bin/python3
'''
Run an interactive QA session using Groq LLM API, concurrent financial data from Finnhub API, article search using Google API, and retrieval augmented generation (RAG).
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
import readline
from bs4 import BeautifulSoup
import finnhub

################################################################################
# LLM functions
################################################################################

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)
finnhub_client = finnhub.Client(
    api_key=os.environ.get("FINN_API_KEY"),
    )

#Google API Key Access
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

#Groq Functions
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
    system = 'Summarize the input text below. Limit the summary to 1 paragraph. Use an advanced reading level similar to the input text, and ensure that all people, places, and other proper names and dates are included in the summary. Only include the summary.'
    return run_llm(system, text, seed=seed)

def get_popular_symbol(input, seed=None):
    """
    Identifies the company's stock ticker based on the user's query.
    If the input lacks a company name, guides the user to provide relevant information.
    Prioritizes common stocks from NASDAQ and NYSE.
    """
    system = '''Identify the company's stock ticker based on the user's query below.
    Prioritize common stocks from NASDAQ and NYSE.
    Return only the stock ticker in your response.'''
    return run_llm(system, input, seed=seed)


def extract_date(input, seed=None):
    '''Uses Finnhub API to get a date range given a user query. Defaults to the past month if no date specified.'''
    system = '''Identify what date range the user is interested in. 
    This will be used to search for articles relevant to the date range the user mentions. 
    Only output a list with two string variables, the first being the start date in YYYY-MM-DD format and the second being the end date also in YYYY-MM-DD format. 
    If the user does not reference any specific dates, output the list with the start date being one month in before today YYYY-MM-DD format and the end date being today in YYYY-MM-DD format.
    Do not include time.'''
    return run_llm(system, input, seed=seed)

def extract_keywords(text, seed=None):
    '''
    This is a helper function for RAG.
    Given an input text, this function extracts the keywords that will be used to perform the search for articles that will be used in RAG.
    '''

    system = """
    Do not answer the question. 
    Only provide a string containing 5-10 of the top keywords relevant to the topic that would benefit a search for articles online relating to the question. 
    Separate each keyword with a space. 
    Prioritize names, actions, and dates in the string of keywords.
    Follow these rules:
    1. Escape or format any special characters (like single quotes, apostrophes, etc.) that could cause problems in a query.
    2. Return the keywords as a single string, formatted such that numbers and special characters do not break any query syntax.
    For example, if the question is: 'Does Bloomberg recommend buying for Apple?', an acceptable output would be: Bloomberg Apple recommendation.
    Another example, if the question is: 'What are some of the challenges Tesla is currently facing?', an acceptable output would be: Tesla recent challenges.
    """
    keywords = run_llm(system, text, seed=seed)
    return keywords

#Finnhub functions
def get_symbol(input):
    '''finds the stock symbol given a user input like Apple using the Finnhub API'''
    return finnhub_client.symbol_lookup(input)

def get_valid_symbol(input):
    """Identifies the most likely stock ticker of interest given an input string using the Finnhub API."""
    ticker = get_popular_symbol(input)
    print(ticker) #testing
    # Ensure the ticker is valid in Finnhub's system
    if (ticker):
        search_results = get_symbol(input)
        if search_results['count'] == 0:
            return "No results found."
        
        # Filter for 'Common Stock'
        common_stocks = [item for item in search_results['result'] if item.get('type') == 'Common Stock']
        
        # Prioritize symbols on major exchanges (e.g., NASDAQ, NYSE)
        major_exchanges = ['NASDAQ', 'NYSE']
        major_stocks = [
            item for item in common_stocks 
            if any(exchange in item.get('displaySymbol', '') for exchange in major_exchanges)
        ]
        
        # Return the best match
        if major_stocks:
            return major_stocks[0]['displaySymbol']
        if common_stocks:
            return common_stocks[0]['displaySymbol']
        if search_results['result']:
            return search_results['result'][0]['displaySymbol']
        
        return "No suitable match found."

def get_quote(ticker):
    '''Gets financial stock information given a stock ticker using Finnhub API and returns it as a string'''
    quote = finnhub_client.quote(ticker)
    # Calculate change and percent change
    quote['d'] = round(quote['c'] - quote['pc'], 2)  # Change = current price - previous close price
    quote['dp'] = round((quote['d'] / quote['pc']) * 100, 2)  # Percent change
    # Format the output string
    output = (
        f"Current price: {quote['c']}, "
        f"Change: {quote['d']}, "
        f"Percent change: {quote['dp']}%, "
        f"High price of the day: {quote['h']}, "
        f"Low price of the day: {quote['l']}, "
        f"Open price of the day: {quote['o']}, "
        f"Previous close price: {quote['pc']}"
    )
    return output

def get_recommendations(ticker):
    """
    Gets stock recommendation trends for a given stock ticker using Finnhub API and returns it as a formatted string.
    """
    trends = finnhub_client.recommendation_trends(ticker)
    # Format the output string
    output = ""
    for trend in trends:
        output += (
            f"Period: {trend['period']}, "
            f"Strong Buy: {trend['strongBuy']}, "
            f"Buy: {trend['buy']}, "
            f"Hold: {trend['hold']}, "
            f"Sell: {trend['sell']}, "
            f"Strong Sell: {trend['strongSell']}\n"
        )
    return output.strip()
    
def get_news(ticker, input):
    '''Gets news articles relating to the Stock ticker using Finnhub API'''
    dates = extract_date(input)
    news_results = finnhub_client.company_news(ticker, _from=dates[0], to=dates[1])
    if news_results is None:
        return "No news results found."
    articles = []
    for row in news_results:
        articles.append({
            'headline': row['headline'],
            'source': row['source'],
            'summary': row['summary'],
            'url': row['url']
                })
    return articles

################################################################################
# helper functions
################################################################################

#Google Functions
def google_search(query, api_key, cse_id, num_results=5):
    """
    Perform a Google Custom Search for articles based on the query.
    Exclude blacklisted domains and prioritize accessible sources.
    """
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {"q": query, "key": api_key, "cx": cse_id, "num": num_results}
    preferred_domains = ["finance.yahoo.com", "reuters.com", "seekingalpha.com", "nasdaq.com"]
    blacklist = ["investors.com", "marketwatch.com", "motleyfool.com"]

    try:
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get("items", [])

        # Filter out blacklisted domains
        filtered_results = [
            {"title": item.get("title"), "link": item.get("link")}
            for item in results
            if all(domain not in item.get("link", "") for domain in blacklist)
        ]

        # Prioritize preferred domains
        prioritized_results = sorted(
            filtered_results,
            key=lambda x: any(domain in x.get("link", "") for domain in preferred_domains),
            reverse=True
        )

        return prioritized_results
    except Exception as e:
        logging.error(f"Error during Google Search: {e}")
        return []

def fetch_article_content(url):
    """
    Fetch and extract readable content from the given URL.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        content = " ".join(p.get_text() for p in paragraphs)
        return content if content.strip() else None
    except requests.exceptions.RequestException as e:
        logging.warning(f"Error fetching content from {url}: {e}")
        return None

################################################################################
# Article Summary Generator
################################################################################

def generate_response(user_query):
    """
    Generate a response by searching for articles and summarizing their content.
    """
    articles = google_search(user_query, GOOGLE_API_KEY, GOOGLE_CSE_ID, num_results=5)
    if not articles:
        return "No relevant articles found. Please refine your query."

    valid_articles = []
    for article in articles:
        title = article["title"] or "No title"
        link = article["link"] or "No link"
        content = fetch_article_content(link)
        if content:
            summary = summarize_text(content)
            valid_articles.append(f"Title: {title}\nURL: {link}\nSummary: {summary}")
        else:
            logging.info(f"Skipping inaccessible article: {link}")

    if not valid_articles:
        return "No accessible articles could be retrieved. Try another query or refine your sources."

    return "\n\n".join(valid_articles)

################################################################################
# rag
################################################################################

def rag(text):
    '''
    This function uses retrieval augmented generation (RAG) to generate an LLM response to the input text.
    '''
    #keywords = extract_keywords(text)
    #sanitized_keywords = keywords.replace("'", "''")
    #print(f"Keywords: {sanitized_keywords}")  # testing

    ticker = get_popular_symbol(text)
    print(f"Stock Ticker: {ticker}")

    quote = get_quote(ticker)
    print(f"Quote: {quote}") #testing

    recommendations = get_recommendations(ticker)
    print(f"Recommendations: {recommendations}") #testing

    article_summaries = generate_response(text)
    #print(f"Article Summaries: {article_summaries}") #testing

    system = """You are a professional stock analyst and advisor tasked with answering user queries based on the provided information. 
    Do not take into account any knowledge outside of the articles in your answer.
    Do not add any extra details, opinions, unnecessary explanations.
    You are not allowed to mention the source of your information. 
    Your responses must be concise, accurate, and directly address the user's question in at most three complete sentences. 
    Answer the user as if you have personally conducted the research and are providing a professional summary of the findings.
    Incorporate relevant insights from the financial data, stock recommendations, and article summaries provided. 
    Stop responding once you have provided the necessary answer.
    """
    system += quote
    #system += "Analyst Recommendations:"
    system += recommendations
    #system += "Articles:"
    system += article_summaries
    system += f"User query: {text}"

    return run_llm(system, text)


################################################################################
# Main Program
################################################################################

if __name__ == "__main__":
   logging.basicConfig(
       format='%(asctime)s %(levelname)-8s %(message)s',
       datefmt='%Y-%m-%d %H:%M:%S',
       level=logging.WARNING,
   )
   print("Please include the name of the company or its ticker and your question in complete sentences.")
   while True:
    try:
        query = input("Stock Recommendation Chatbot: ").strip()
        if query.lower() in {"exit", "quit"}:
            print("Exiting the chatbot. Goodbye!")
            break
        if query:
            print(rag(query))
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")