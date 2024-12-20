#!/bin/python3
"""
Run an interactive Question-Answering (QA) chatbot session that integrates multiple advanced functionalities:
- Leverages the Groq LLM API for natural language processing and intelligent responses.
- Utilizes the Finnhub API to retrieve real-time financial data for market insights.
- Performs article searches through the Google API for relevant, up-to-date information.
- Implements Retrieval-Augmented Generation (RAG) for enhanced context-driven answers.
"""

import logging
import re
import groq
from groq import Groq
import os
import requests
import readline
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import finnhub
import sys
import ast

################################################################################
# Core LLM and API Functions
################################################################################

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)
finnhub_client = finnhub.Client(
    api_key=os.environ.get("FINN_API_KEY"),
    )
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
    "Summarizes the input text into a paragraph and keeps relevant stock information"
    system = '''Summarize the input text below.
    Limit the summary to 1 paragraph.
    Use an advanced reading level similar to the input text, and ensure that all people, places, and other proper names and dates are included in the summary.
    When possible, keep buy/hold/sell ratings, challenges the company faces, and financial information in the summary.
    Only include the summary.'''
    return run_llm(system, text, seed=seed)

def get_popular_symbol(input, seed=None):
    '''
    Identifies the company's stock ticker based on the user's query.
    If the input lacks a company name, returns 'None'
    Prioritizes common stocks from NASDAQ and NYSE.
    Example:
    >>> get_popular_symbol("Apple")
    "['AAPL']"
    >>> get_popular_symbol("Tesla")
    "['TSLA']"
    >>> get_popular_symbol("Microsoft")
    "['MSFT']"
    >>> get_popular_symbol("Is Tesla a good buy?")
    "['TSLA']"
    >>> get_popular_symbol("Is Google better than Amazon, Microsoft, and Apple?")
    "['GOOGL', 'AMZN', 'MSFT', 'AAPL']"
    >>> get_popular_symbol("")
    'None'
    '''
    if input=="":
        return 'None'
    system = """Identify what company the user is interested in based on the query below.
    Prioritize common stocks from NASDAQ and NYSE.
    If no specific company or tickers are included, only give at most 2 companies that relate to the query.
    Do not include any extra details, opinions, or unecessary explanations.
    Return the stock tickers of the companies as a python list.
    If only one company is in the query return the ticker for that one company.
    Examples: 
    "Is Tesla a good buy?" A good response is ['TSLA'].
    "If I think LLMs are good for the future, which stocks should I buy?" A good response is ['APPL', 'MSFT']
    "Is Google better than Amazon, Microsoft, and Apple" A good response is ['GOOGL', 'AMZN', 'MSFT', 'AAPL']
    """
    return run_llm(system, input, seed=seed)

def get_quote(ticker, mock_data=None):
    """
    Gets financial stock information given a stock ticker using Finnhub API.

    Args:
        ticker (str): The stock ticker symbol.
        mock_data (dict, optional): Mocked API response for testing.

    Returns:
        str: A string describing the stock's current price and changes.

    Example:
    >>> mock_data = {'c': 150.0, 'pc': 145.0, 'h': 155.0, 'l': 140.0, 'o': 145.0}
    >>> get_quote("AAPL", mock_data)
    'Current price: 150.0, Change: 5.0, Percent change: 3.45%, High price of the day: 155.0, Low price of the day: 140.0, Open price of the day: 145.0, Previous close price: 145.0'
    """
    # Use mock data if provided, otherwise call the API
    quote = mock_data if mock_data else finnhub_client.quote(ticker)
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


################################################################################
# Google and Article Processing Functions
################################################################################

def google_search(query, api_key, cse_id, num_results=5, date_restrict="m1"):
    """
    Perform a Google Custom Search for articles based on the query.
    Exclude blacklisted domains and prioritize accessible sources.
    Adjust date_restrict parameter according to preference:
    dN: last N days,
    wN: last N weeks,
    mN: last N months
    yN: last N years 
    """
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": cse_id,
        "num": num_results,
        "dateRestrict": date_restrict  # Filter results based on recency
       }
    preferred_domains = ["finance.yahoo.com", "bloomberg.com", "morningstar.com", "cnbc.com", "seekingalpha.com", "nasdaq.com"]
    blacklist = ["investors.com", "marketwatch.com", "reuters.com", "motleyfool.com"]

    try:
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get("items", [])

        # Filter out blacklisted domains
        filtered_results = [
            {
                "title": item.get("title"),
                "link": item.get("link"),
                "date": item.get("pagemap", {}).get("metatags", [{}])[0].get("article:published_time")
            }
            for item in results
            if all(domain not in item.get("link", "") for domain in blacklist)
        ]

        # Validate and parse dates
        for result in filtered_results:
            date_str = result.get("date")
            try:
                if date_str:
                    result["date"] = datetime.fromisoformat(date_str).isoformat()
                else:
                    result["date"] = None  # Handle missing dates
            except ValueError:
                logging.warning(f"Invalid date format for article: {result}")
                result["date"] = None
            
        # Sort results: prioritize by preferred domains and then by date
        def sort_key(result):
            in_preferred = any(domain in result.get("link", "") for domain in preferred_domains)
            date = datetime.fromisoformat(result["date"]).replace(tzinfo=None) if result.get("date") else datetime.min
            return (in_preferred, date)

        sorted_results = sorted(filtered_results, key=sort_key, reverse=True)
        return sorted_results

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
# Article Search and Summary Generator
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
            summary = summarize_text(content[:1000])
            valid_articles.append(f"Title: {title}\nURL: {link}\nSummary: {summary}")
        else:
            logging.info(f"Skipping inaccessible article: {link}")

    if not valid_articles:
        return "No accessible articles could be retrieved. Try another query or refine your sources."

    return "\n\n".join(valid_articles)

################################################################################
# RAG Handler
################################################################################

def rag(text):
    '''
    This function uses retrieval augmented generation (RAG) to generate an LLM response to the input text.

    >>> rag("")
    'Please provide a company name or a stock symbol in your query.'
    '''
    if text == "":
        return 'Please provide a company name or a stock symbol in your query.'
    ticker = get_popular_symbol(text)
    if ticker == 'None':
        return 'Please provide a company name or a stock symbol in your query.'

    system = """You are a professional stock analyst and advisor tasked with answering user queries based on the provided information. 
    Do not take into account any knowledge outside of the financial data, stock recommendation, or provided article summaries in your answer.
    Do not add any extra details, opinions, or unecessary explanations.
    You are not allowed to mention the source of your information. 
    Directly address the user's question via concise and accurate incorporation of relevant information.
    Answer in at most four complete sentences like you are giving a professional report via conversation. 
    Answer like you personally conducted the research yourself.
    You should only use the stock recommendations if no specific source is requested since it is aggregated across many sources.
    Include 'Yes' or "No' in your answer when applicable.
    Stop responding once you have provided the necessary answer.
    """

    converted_list = ast.literal_eval(ticker)
    for stock in converted_list:
        print(f"Stock Ticker:\n{stock}\n")
        quote = get_quote(stock)
        print(f"Quote:\n{quote}\n") 
        system += f"Quote for {stock}:\n{quote}"

        recommendations = get_recommendations(stock)
        print(f"Aggregated Analyst Ratings for {stock}:\n{recommendations}\n") 
        system += f"Aggregated Analyst Ratings for {stock}:\n{recommendations}"

    article_summaries = generate_response(text)
    print(f"Article Summaries:\n{article_summaries}\n") 
    system += article_summaries

    system += f"User query: {text}"

    print("Chatbot Answer:\n")
    return run_llm(system, text)


################################################################################
# Main Interactive Chatbot Program
################################################################################

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.WARNING,
    )

    if len(sys.argv) > 1 and sys.argv[1] == "doctests":
        import doctest
        doctest.testmod(verbose=True)
    else:
        print("Please include the name of the company or its ticker and your question in complete sentences.")
        print("Enter 'exit' or 'quit' to end the conversation.")
        while True:
            try:
                query = input("Chatbot>: ").strip()
                if query.lower() in {"exit", "quit"}:
                    print("Exiting the chatbot. Goodbye!")
                    break
                if query:
                    response = rag(query)
                    print(response, "\n\n---\n")
                else:
                    print("Please enter a valid question or command.")
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")