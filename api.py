import os
import requests
import logging
from bs4 import BeautifulSoup
from groq import Groq

# API Keys from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq LLM client
LLM_CLIENT = Groq(api_key=GROQ_API_KEY)

################################################################################
# Helper Functions
################################################################################

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

def summarize_text_with_llm(content):
    """
    Generate a summary using LLM for the given content.
    """
    system_prompt = "Summarize the following content in a concise paragraph:"
    try:
        chat_completion = LLM_CLIENT.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content},
            ],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        logging.warning(f"LLM summarization failed: {e}")
        return fallback_summarize(content)

def fallback_summarize(content):
    """
    Simple fallback summarization method using text slicing.
    """
    sentences = content.split(".")
    summary = ". ".join(sentences[:3]) + "..." if sentences else "No content available for fallback summarization."
    return summary

################################################################################
# Response Generation
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
            summary = summarize_text_with_llm(content)
            valid_articles.append(f"Title: {title}\nURL: {link}\nSummary: {summary}")
        else:
            logging.info(f"Skipping inaccessible article: {link}")

    if not valid_articles:
        return "No accessible articles could be retrieved. Try another query or refine your sources."

    return "Top Articles:\n\n" + "\n\n".join(valid_articles)

################################################################################
# Main Program
################################################################################

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.WARNING,
    )

    print("Stock Recommendation Chatbot: Ask your question about stocks or finance.")
    while True:
        try:
            query = input("Enter your question: ").strip()
            if query.lower() in {"exit", "quit"}:
                print("Exiting the chatbot. Goodbye!")
                break
            if query:
                response = generate_response(query)
                print(f"\n{response}\n")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
