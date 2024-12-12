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
from datetime import datetime
import finnhub

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
    system = '''Summarize the input text below.
    Limit the summary to 1 paragraph.
    Use an advanced reading level similar to the input text, and ensure that all people, places, and other proper names and dates are included in the summary.
    When possible, keep buy/hold/sell ratings, challenges the company faces, and financial information in the summary.
    Only include the summary.'''
    return run_llm(system, text, seed=seed)

def get_popular_symbol(input, seed=None):
    """
    Identifies the company's stock ticker based on the user's query.
    If the input lacks a company name, guides the user to provide relevant information.
    Prioritizes common stocks from NASDAQ and NYSE.
    """
    system = '''Identify the company's stock ticker based on the user's query below.
    Prioritize common stocks from NASDAQ and NYSE.
    You are only allowed to include the stock ticker in your response.'''
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
    preferred_domains = ["finance.yahoo.com", "bloomberg.com", "morningstar.com", "seekingalpha.com", "nasdaq.com"]
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

        # Sort results by publication date (if available)
        sorted_results = sorted(
            filtered_results,
            key=lambda x: datetime.fromisoformat(x["date"]) if x.get("date") else datetime.min,
            reverse=True
        )

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
            summary = summarize_text(content)
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
    '''

    ticker = get_popular_symbol(text)
    print(f"Stock Ticker: {ticker}")

    quote = get_quote(ticker)
    print(f"Quote: {quote}") #testing

    recommendations = get_recommendations(ticker)
    print(f"Recommendations: {recommendations}") #testing

    article_summaries = generate_response(text)
    print(f"Article Summaries: {article_summaries}\n") #testing

    system = """You are a professional stock analyst and advisor tasked with answering user queries based on the provided information. 
    Do not take into account any knowledge outside of the articles in your answer.
    Do not add any extra details, opinions, unnecessary explanations.
    You are not allowed to mention the source of your information. 
    Your responses must be concise, accurate, and directly address the user's question in at most three complete sentences. 
    Answer the user as if you have personally conducted the research and are providing a professional summary of the findings.
    Incorporate relevant insights from the financial data, stock recommendations, and article summaries provided.
    You should only use the stock recommendations if no specific source is requested since it is aggregated across many sources.
    Include 'Yes' or "No' in your answer when applicable.
    Stop responding once you have provided the necessary answer.
    """
    system += quote
    system += recommendations
    system += article_summaries
    system += f"User query: {text}"

    return run_llm(system, text)


################################################################################
# Main Interactive Chatbot Program
################################################################################

if __name__ == "__main__":
   import doctest  
   doctest.testmod(verbose=True)
   logging.basicConfig(
       format='%(asctime)s %(levelname)-8s %(message)s',
       datefmt='%Y-%m-%d %H:%M:%S',
       level=logging.WARNING,
   )
   print("Please include the name of the company or its ticker and your question in complete sentences.\nEnter 'exit' or 'quit' to end the conversation.")
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