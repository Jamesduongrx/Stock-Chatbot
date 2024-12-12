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

This chatbot is built to offer precise, actionable advice to assist users in navigating complex financial landscapes efficiently. Whether you’re preparing an investment pitch or looking for real-time market insights, the Stock Recommendation Chatbot provides the tools and knowledge you need.

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
Stock Recommendation Chatbot: Should I buy Tesla Stock

Stock Ticker:
TSLA

Quote:
Current price: 424.77, Change: 23.78, Percent change: 5.93%, High price of the day: 424.88, Low price of the day: 402.38, Open price of the day: 409.7, Previous close price: 400.99

Recommendations: 
Period: 2024-12-01, Strong Buy: 10, Buy: 18, Hold: 19, Sell: 9, Strong Sell: 4
Period: 2024-11-01, Strong Buy: 10, Buy: 17, Hold: 21, Sell: 8, Strong Sell: 4
Period: 2024-10-01, Strong Buy: 10, Buy: 17, Hold: 20, Sell: 8, Strong Sell: 4
Period: 2024-09-01, Strong Buy: 10, Buy: 16, Hold: 21, Sell: 8, Strong Sell: 4

Based on the provided data, there are varying opinions on whether to buy Tesla stock. Some analysts, like Bank of America, recommend a buy, citing Tesla's strategic initiatives and self-funding status. Others, like JPMorgan, are more cautious, downgrading their rating to underweight due to concerns about the sustainability of Tesla's strong earnings. Additionally, some users on Reddit have expressed concerns about Elon Musk's priorities, potentially impacting Tesla's long-term success. However, Kiplinger suggests holding, citing a divided analyst consensus and a 20% decline implied by the average price target. Considering the mixed signals, it's essential to evaluate your individual circumstances, investment goals, and risk tolerance before making a decision.
```

### Chatbot Test Cases

#### Test Case 1: Stock Recommendation Matching

This test evaluates the chatbot’s ability to match stock recommendations (e.g., “buy,” “sell”) based on a specific source (e.g., Bloomberg). Run the test case using:

```bash
$ python3 test_chatbot1.py
```

#### Output:

```
Accuracy: 5/6 (83.33%)
```

#### Test Case 2: Stock Recommendation Matching

This test evaluates the chatbot’s ability to extract industry-related and financial information for a company by identifying relevant keywords from a query. Run the test case using:

```bash
$ python3 test_chatbot2.py
```

#### Output:

```
Accuracy: 5/7 (71.43%)
```
