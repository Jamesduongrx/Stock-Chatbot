![](https://github.com/Jamesduongrx/Stock-Chatbot/actions/workflows/tests.yml/badge.svg)

# Stock Recommendation Chatbot: Overview

The **Stock Recommendation Chatbot** is an intelligent assistant designed to deliver stock recommendations and pitch-ready investment insights. By leveraging real-time financial data, news articles, and user inputs, it supports decision-making for buying, holding, or selling stocks, as well as answering general market-related questions.

## Key features include:
	1.	**Real-Time Analysis**
        Processes financial news, company performance, and market trends to provide timely and accurate insights.
	2.	**User-Centric Design**
        Tailors recommendations based on user queries and preferences.
	3.	**Investment Pitch Support**
        Generates insights ready for pitching to investment clubs or for personal strategies.

This chatbot is built to offer precise, actionable advice to assist users in navigating complex financial landscapes efficiently.

## Getting Started

# Prerequisites

Before proceeding, check that you have the following installed:

- Python 3.8 or 3.9
- Groq API key
- Finnhub API Key
- Google API Key
- GOOGLE CSE ID

# Installation
1. **Clone the repository:**
```
$ git clone https://github.com/Jamesduongrx/Stock-Chatbot
```

2. **Create a virtual environment:**

```
$ python3.9 -m venv venv
$ source venv/bin/activate
```

3. **Install the necessary Python packages:**

```
$ pip3 install -r requirements.txt
```

4. **Set up a GROQ API key:**
    - Create your GROQ API key at https://groq.com/
    - Create your Google API key at https://cloud.google.com/docs/authentication/api-keys
    - Create your Google CSE ID key at https://programmablesearchengine.google.com/about/
    - Create your Finnhub API key at https://finnhub.io/
    - Create a `.env` file in the project root directory and add your Groq API key.
    
    ```
    GROQ_API_KEY=your_groq_api_key_here
    GOOGLE_API_KEY=your_google_api_key_here
    GOOGLE_CSE_ID=your_google_cse_id_here
    FINN_API_KEY=your_finnhub_api_key_here

    ```

    - Export the environmental variables:

        ```
        $ export $(cat .env)
        ```

## Running the Application
Once your environment is set up, you can start Chatbot:
```
$ python3 chatbot.py
```

### Example Usage
After starting the application, you can interact with it via the command line interface:

```
$ python3 chatbot.py 
Stock Recommendation Chatbot: Should I buy Tesla Stock

Stock Ticker: TSLA
Quote: Current price: 424.77, Change: 23.78, Percent change: 5.93%, High price of the day: 424.88, Low price of the day: 402.38, Open price of the day: 409.7, Previous close price: 400.99
Recommendations: Period: 2024-12-01, Strong Buy: 10, Buy: 18, Hold: 19, Sell: 9, Strong Sell: 4
Period: 2024-11-01, Strong Buy: 10, Buy: 17, Hold: 21, Sell: 8, Strong Sell: 4
Period: 2024-10-01, Strong Buy: 10, Buy: 17, Hold: 20, Sell: 8, Strong Sell: 4
Period: 2024-09-01, Strong Buy: 10, Buy: 16, Hold: 21, Sell: 8, Strong Sell: 4
Based on the provided data, there are varying opinions on whether to buy Tesla stock. Some analysts, like Bank of America, recommend a buy, citing Tesla's strategic initiatives and self-funding status. Others, like JPMorgan, are more cautious, downgrading their rating to underweight due to concerns about the sustainability of Tesla's strong earnings. Additionally, some users on Reddit have expressed concerns about Elon Musk's priorities, potentially impacting Tesla's long-term success. However, Kiplinger suggests holding, citing a divided analyst consensus and a 20% decline implied by the average price target. Considering the mixed signals, it's essential to evaluate your individual circumstances, investment goals, and risk tolerance before making a decision.
```