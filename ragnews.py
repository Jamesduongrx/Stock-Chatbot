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

google_api_key = os.getenv("GOOGLE_CSE_ID")

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
    system = 'Summarize the input text below. Limit the summary to 1 paragraph. Use an advanced reading level similar to the input text, and ensure that all people, places, and other proper names and dates are included in the summary. The summary should be in English. Only include the summary.'
    return run_llm(system, text, seed=seed)

def extract_company(keywords, seed=None):
    system = '''Identify what company the user is interested in learning more about.
    Only return that company in your output.
    If the user does not reference any company, return nothing.
    The output of this function will be used in a get_most_popular_symbol() function from Finnhub API to find the company's stock ticker.'''
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
    Another example, if the question is: 'What are some of the challenges Tesla is currently facing?', an acceptable output would be: Tesla recent challenges.
    """
    keywords = run_llm(system, text, seed=seed)
    return keywords

#Finnhub functions
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

def google_search(query, api_key, cse_id, num_results=5):
   """
   Perform a Google Custom Search for articles based on the query.
   """
   try:
       search_url = "https://www.googleapis.com/customsearch/v1"
       params = {'q': query, 'key': api_key, 'cx': cse_id, 'num': num_results}
       response = requests.get(search_url, params=params)
       response.raise_for_status()
       results = response.json().get('items', [])
      
       articles = []
       for item in results:
           title = item.get("title", "No title")
           link = item.get("link", "No link")
           articles.append(f"{title} (URL: {link})")
       return articles
   except Exception as e:
       logging.error(f"Error during Google Search:")
       return []

################################################################################
# Interactive QA Session
################################################################################

'''def generate_response(user_query):
   """
   Generate a chatbot response for the user's query using Google Search.
   """
   articles = google_search(user_query, GOOGLE_API_KEY, GOOGLE_CSE_ID, num_results=5)
   if not articles:
       return "No relevant articles found. Please try again with a different query."

   return "Top Articles:\n" + "\n".join(articles)'''

################################################################################
# rag
################################################################################

def rag(text):
    '''
    This function uses retrieval augmented generation (RAG) to generate an LLM response to the input text.
    The db argument should be an instance of the `ArticleDB` class that contains the relevant documents to use.
    '''
    keywords = extract_keywords(text)
    sanitized_keywords = keywords.replace("'", "''")
    print(f"Keywords: {keywords}")  # Debug the keywords
    print(f"Retrieved {len(articles)} articles")

    ticker = get_most_popular_symbol(sanitized_keywords)
    articles = get_news(ticker, sanitized_keywords)
    quote = get_quote(ticker)

    system = """You are a professional stock analyst tasked with answering questions based solely on the provided articles. 
    Do not take into account any knowledge outside of the articles in your answer.
    Your responses should be concise, accurate, and directly address the question. 
    You must summarize key information from the articles clearly in at most three complete sentences. 
    Do not add any extra details, opinions, or unnecessary explanations. 
    You are not allowed to talk about or mention the source of your information or articles in your answer.
    Present the information as if you have done the research yourself.
    Stop responding once you have provided the necessary answer."""

    system += ("Here is some concurrent financial information regarding the user's stock of interest. Incorporate this information into your response whenever relevant and possible.",
        "Current price", str(quote['c']), 
        "Change", str(quote['d']),
        "Percent change", str(quote['dp']),
        "High price of the day", str(quote['h']),
        "Low price of the day", str(quote['l']),
        "Open price of the day", str(quote['o']),
        "Previous close price", str(quote['pc'])
        )

    string_articles = ""
    for article in articles:
        if article['text']:
            string_articles += (f"Title: {article['headline']}\nContent: {article['summary']}\n\n")
        else:
            logging.warning(f"Article with title '{article['headline']}' has no text content.")
    if not string_articles:
        return "No relevant articles with text found for the query."
    string_articles = summarize_text(string_articles)
    system += string_articles
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

while True:
    text = input('Stock Chatbot> ')
    if len(text.strip()) > 0:
        output = rag(text)
        print(output)