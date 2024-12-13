# Stock Recommendation Chatbot 

[![Tests](https://github.com/Jamesduongrx/Stock-Chatbot/actions/workflows/tests.yml/badge.svg)](https://github.com/Jamesduongrx/Stock-Chatbot/actions/workflows/tests.yml)

The **Stock Recommendation Chatbot** is an AI-powered assistant designed to deliver stock recommendations and pitch-ready investment insights. By leveraging real-time financial data, news articles, and user inputs, it supports decision-making for buying, holding, or selling stocks, as well as answering general market-related questions.

## Key Features Include:
1.	**Real-Time Analysis**
    Processes concurrent financial news, company performance, and market trends to provide timely and accurate insights.
2.	**User-Centric Design**
    Tailors recommendations based on user queries and preferences.
3.	**Investment Pitch Support**
    Generates insights ready for pitching to investment funds or for personal strategies.
4.	**Advanced Functionalities**
    * Leverages Groq LLM API: Delivers natural language processing and intelligent responses.
	* Utilizes Finnhub API: Retrieves real-time financial data for market analysis and insights.
	* Performs Article Searches with Google API: Incorporates the latest news and trends.
	* Implements Retrieval-Augmented Generation (RAG): Enhances context-driven answers by combining retrieved data with AI-generated insights.

This chatbot is built to offer precise, actionable advice to assist users in navigating intricate financial landscapes efficiently.

---

## Getting Started

### Prerequisites

Before proceeding, check that you have the following installed:

- Python 3.8 or 3.9
- Groq API key
- Finnhub API key
- Google API key
- GOOGLE CSE ID

### Installation
1. **Clone the repository:**

```bash
$ git clone https://github.com/Jamesduongrx/Stock-Chatbot
```

2. **Create a virtual environment:**

```bash
$ python3.9 -m venv venv
$ source venv/bin/activate
```

3. **Install the necessary Python packages:**

```bash
$ pip3 install -r requirements.txt
```

4. **Set up a GROQ API key:**
    - [Create your GROQ API key](https://groq.com/)
    - [Create your Google API key](https://cloud.google.com/docs/authentication/api-keys)
    - [Create your Google CSE ID](https://programmablesearchengine.google.com/about/)
    - [Create your Finnhub API key](https://finnhub.io/)
    - Create a `.env` file in the project root directory and add your Groq API key.
    
    ```env
    $ GROQ_API_KEY=your_groq_api_key_here
    $ GOOGLE_API_KEY=your_google_api_key_here
    $ GOOGLE_CSE_ID=your_google_cse_id_here
    $ FINN_API_KEY=your_finnhub_api_key_here
    ```

    - Export the environmental variables:

        ```bash
        $ export $(cat .env)
        ```

### Running the Application
Once your environment is set up, you can start Chatbot:

```bash
$ python3 chatbot.py
```

### Example Usage
After starting the application, you can interact with it via the command line interface:

```bash
$ python3 chatbot.py
```

#### Example Interaction:

```
Stock Recommendation Chatbot: Is Amazon a good stock to buy?

Stock Ticker:
AMZN

Quote:
Current price: 228.97, Change: -1.29, Percent change: -0.56%, High price of the day: 231.09, Low price of the day: 227.63, Open price of the day: 229.83, Previous close price: 230.26

Article Summaries:
Title: Better AI Stock to Buy Today: Dell Technologies vs. Amazon
URL: https://finance.yahoo.com/news/better-ai-stock-buy-today-120000918.html
Summary: Dell Technologies and Amazon are among the companies benefiting from the growing popularity of artificial intelligence, particularly generative AI. Dell has witnessed strong growth, specifically in the AI server market, with its infrastructure solutions segment reporting a 38% increase in revenue to $11.6 billion in its last reported quarter. Within this segment, servers and networking revenue surged 80% to $7.7 billion. Meanwhile, Amazon has also been leveraging AI capabilities, although its focus is more on development and incorporation into its various products. Both companies have substantial potential, but Dell's strong growth in the AI server market makes it an attractive option for investors seeking to capitalize on this trend.

Title: AMZN Stock vs. GOOG Stock: Which Is the Better Buy Today ...
URL: https://www.cabotwealth.com/daily/growth-stocks/amzn-stock-goog-stock-better-buy
Summary: Here is a summary of the input text in 1 paragraph, written at an advanced reading level with proper names, dates, and financial information included:

Amazon (AMZN) and Alphabet (GOOG) are two of the world's most recognizable brands, with a long-term trajectory still favorably inclined. Despite being battered by the growth stock sell-off of 2022, both stocks have rebounded impressively, with GOOG rising 99% since 2023's start and AMZN surging 168% over the same period. Over five years, GOOG has climbed 163%, outpacing AMZN's 157% gain and the S&P 500's 93%. As both companies have delivered exceptional returns, the question arises: can they replicate or exceed this performance over the next five years? Despite their impressive track records, it's unlikely they will continue to grow at this pace indefinitely, though it would be foolhardy to doubt their potential.

Title: Could Buying Amazon Stock Today Set You Up for Life? | The ...
URL: https://www.fool.com/investing/2024/11/16/could-buying-amazon-stock-today-set-you-up-for-lif/
Summary: The Motley Fool, founded in 1993, is a financial services company that strives to make the world smarter, happier, and richer through its various platforms. The company reaches millions of people each month via its premium investing solutions, free guidance and market analysis on Fool.com, personal finance education, top-rated podcasts, and non-profit The Motley Fool Foundation. With its extensive resources, The Motley Fool helps individuals make informed investment decisions, with the option to also access top analyst recommendations, in-depth research, and investing resources through its premium membership.

Chatbot Answer:

Based on the current market data and analyst ratings, Amazon (AMZN) shows a Strong Buy signal with 21 analysts recommending a Strong Buy, 50 analysts recommending a Buy, and 0 analysts recommending a Sell or Strong Sell. The stock's current price is $228.97, with a recent strong growth trend in its AI server market and a solid track record of returns. 

---
```

### Chatbot Test Cases

To test, you may have to update `test_cases1.json` to reflect concurrent market trends if the sources have changed their recommendation for the given company. Similarly, you may have to update `test_cases2.json` to reflect concurrent challenges the respective companies are facing.

#### Test Case 1: Stock Recommendation Matching

This test evaluates the chatbot’s ability to match stock recommendations (e.g., “buy,” “sell”) based on a specific source (e.g., Bloomberg). Run the test case using:

```bash
$ python3 test_chatbot1.py
Accuracy: 5/6 (83.33%)
```
To test, you may have to update `test_cases1.json` to reflect concurrent market trends if the sources have changed their recommendation for the given company. 
Similarly, you may have to update `test_cases2.json` to reflect concurrent challenges the respective companies are facing.

#### Test Case 2: Stock Recommendation Matching

This test evaluates the chatbot’s ability to extract industry-related and financial information for a company by identifying relevant keywords from a query. Run the test case using:

```bash
$ python3 test_chatbot2.py
Accuracy: 5/7 (71.43%)
```
