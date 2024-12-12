# Stock Recommendation Chatbot ![](https://github.com/Jamesduongrx/Stock-Chatbot/workflows/tests/badge.svg?dummy=timestamp)

## Overview

The Stock Recommendation Chatbot is a chatbot assistant designed to provide stock recommendations and pitch-ready investment insights. By analyzing real-time financial data, news articles, and user inputs, the chatbot can help users make informed decisions about buying, holding, or selling stocks as well as general market or stock questions.

With its ability to analyze recent events, company performance, and market trends, the chatbot delivers concise insights tailored to user queries. 

## Key Features

- Retrieval-Augmented Generation (RAG): Efficiently fetches relevant articles to improve response accuracy.
- News Integration: Processes user queries using a dynamic database of news articles.
- Groq API Powered: Leverages Groq models for natural language processing.

## Getting Started

# Prerequisites

Before proceeding, check that you have the following installed:

- Python 3.8 or 3.9
- A Groq API key (instructions below)

# Installation

To get started with `ragnews`, follow these steps to set up your
development environment and run the application:

1. **Clone the repository:**
```
$ git clone https://github.com/EthanTu2/ragnews.git
$ cd ragnews
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
    - Create an API key at https://groq.com/
    - Create a `.env` file in the project root directory and add your Groq API key.
    
    ```
    GROQ_API_KEY=your_api_key_here
    ```

    - Export the environmental variables:

        ```
        $ export $(cat .env)
        ```

## Running the Application
Once your environment is set up, you can start RAGNews:
```
$ python3 ragnews.py
```

### Example Usage
After starting the application, you can interact with it via the command line interface:

```
$ python3 ragnews.py 
ragnews> What is the current democratic presidential nominee?
The current Democratic presidential nominee is Kamala Harris.
```
