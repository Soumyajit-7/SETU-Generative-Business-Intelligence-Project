# SETU-Generative-Business-Intelligence-Project
SETU GEN BI summer Internship Project Featuring Intelligent SQL bots with a Visual Twist in an Interactive WebAPP

# Conversational Generative BI Dashboard

This project is a prototype of a **Conversational Generative BI Dashboard** built for a digital event-organizing platform. It allows users to query a database in natural language and get results in tabular or graphical format using a combination of LangChain, SQL databases, and various LLMs (Large Language Models).

## Project Overview

The client requested a dashboard for event insights, but instead of selecting predefined KPIs, users can ask prompt-based questions and get relevant responses. The prototype interacts with 11 database tables and uses generative AI to translate natural language queries into efficient SQL statements.

### Key Features

- **Natural Language Querying**: Ask questions in natural language, and the system converts them into optimized SQL queries.
- **Event Data Insights**: Analyze event data related to booths, speakers, zones, and more.
- **Visualization Support**: Results are displayed in both table and chart formats for easy interpretation.
- **Generative AI Integration**: Powered by LangChain, Groq, and Google Generative AI for conversational intelligence.

### Setup Instructions:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Soumyajit-7/SETU-Generative-Business-Intelligence-Project
   ```
2. **Download and Unzip the database from**:
   ```URL
   https://github.com/Soumyajit-7/Datasets/blob/main/event-tech.zip
   ```
3. **Setup the Conda environment(Install Anaconda First and use Anaconda Powershell Prompt for a streamlined experience)**:
   ```bash
   conda create --name genbi_env python=3.10
   conda activate genbi_env
   ```
4. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **API key setup**:
   Modify the .env file with your own API keys:
    - Get the GOOGLE_API_KEY from ``` https://ai.google.dev/gemini-api?gad_source=1&gclid=CjwKCAjwxY-3BhAuEiwAu7Y6szZeDDr_4U21aTgwJ2PixwX3UB99KYMDuKutWXB7Y5WdXSY_VW-xoBoC60kQAvD_BwE ```
    - Get the GROQ_API_KEY from ``` https://console.groq.com/keys ```
    - Get the LANGCHAIN_API_KEY from ``` https://docs.smith.langchain.com/how_to_guides/setup/create_account_api_key#api-keys ```
6. **Run the Webapp**:
   run the command to start the streamlit app
   ```bash
   streamlit run Sqlite_Lang_pandasAI2.py --server.enableXsrfProtection false
   ```
7. Enjoy the Webapp:
   Once the Webapp is running on localhost, enter the path to your extracted .db file.
   Now you can explore and interact with the web app!

## Technology Stack

- **Python**: Core programming language
- **LangChain**: Framework for interacting with LLMs
- **Streamlit**: Web interface for real-time interaction
- **SQLite**: Database for storing and querying event data
- **Google Generative AI & Groq**: AI models for language processing
- **PandasAI**: Assists with visual and chart creation.
- **Logging**: Logs all interactions and SQL queries for monitoring

## How It Works

1. **Database Initialization**: The SQLite database is initialized with event-related tables such as accounts, booths, events, and segments.
2. **Natural Language Input**: Users provide input in the form of natural language queries via the Streamlit interface.
3. **SQL Query Generation**: The input is processed by an LLM, which converts the query into an SQL command using the database schema.
4. **Data Retrieval**: The SQL command is executed on the SQLite database, and the result is fetched.
5. **Display Results**: Results are shown in tabular format or as visual charts based on user preference.
