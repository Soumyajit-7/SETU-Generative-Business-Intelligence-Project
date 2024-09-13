import json
import requests
import base64
import uuid
from dotenv import load_dotenv
import os
import random
import pandas as pd
import streamlit as st
import sqlite3
import logging
from pandasai import Agent
from pandasai.llm import LLM
import langchain_groq
from langchain_groq.chat_models import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import tempfile
import time
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

model = ChatGroq(
    api_key = GROQ_API_KEY,
    model_name = "llama3-70b-8192"
)
# Setup logging
logging.basicConfig(filename="sqlite2_logs.log", level=logging.INFO, 
                    format="%(asctime)s %(levelname)s %(message)s")

user_defined_path = f"images/{uuid.uuid4()}"
def save_dataframe(df, save_path=None):
    if save_path is None:
        temp_dir = tempfile.gettempdir()
        save_path = os.path.join(temp_dir, "saved_data.csv")
    df.to_csv(save_path, index=False)
    return save_path
# Create the directory if it doesn't exist
if not os.path.exists("images"):
    os.makedirs("images")

if "data" not in st.session_state:
    st.session_state.data = None 

def save_dataframe(df, save_path="saved_data.csv"):
    df.to_csv(save_path, index=False)
    return save_path
# Broad description of the database schema
BROAD_DESCRIPTION = """
You are working for a Digital event organising client’s platform which they offer to B2B 
clients to organise large-scale events. Nasscom has subscribed to their platform and 
organised 4 events. 
Events can have various zones like  
EXPO 
LOBBY 
NETWORKING 
SCHEDULE 
STAGE 
TABLE 
For example, an expo is a zone where companies showcase their products or services to 
other attendees. The lobby is an area where registration and other welcome activities are 
mainly held. The stage is where all the speaking, round table, panel discussion etc take 
place.  
NASSCOM after conducting 4 events, has gone back to the client and asked them to 
share with them a dashboard that will reflect various insights from these events. Since 
NASSCOM is a large organisation, it became very difficult for them to come up with a 
static list of KPIs to select from, instead, they asked could you create a Generative 
conversational dashboard, which people can use to ask prompt-based questions in 
natural languages and deliver results in tabular as well as in suitable charts?  
Therefore, the client has reached out to you with 11 of their tables from their database 
and asking you to develop a prototype of a Conversational Generative BI dashboard 

The database schema consists of the following tables and columns:

Account Table :

account_id: Alpha-Numeric Account ID 
length_id: Length of the ID 
email: Email id of the users (it has been masked for the security of the PII information) 
createdat: The date when the account was registered 
updatedat: The date when any change in the account details done 
roles: The possible ROLE(S) a user has assumed in multiple events they have attended 
highestauthority: highest authority among the roles assumed. Authority is ideally a role based authority, for example, the organiser has the highest authority, while anattendees has the lowest authority. 
status: A user can be active or invited. When invited, they have to accept the invite and authenticate themselves, which is when their status become active. 
headline: Headline, that will be shown when the user is active on the screen. 
company: Name of the company 
designation: User's designation 
isguestaccount: Boolean (TRUE, FALSE) 
 

Booth table :

booth_id: Unique ID of Booths 
event_id: Event ID associated with where the Booth is hosted 
name: Name of the Booth 
tagline: Tagline of the Booth (if any) 
description: Description of the Booth (if any) 
createdat_time: Time when the booth was created 
createdat_date: Date when the booth was created 
updatedat_time: Time when the booth was updated 
updatedat_date: Date when the booth was updated 
booth_size: Size of the Booth 
booth_order: Relative index of the Booth 
brand_nameName of the company or Brand for which the booth was taken or which brand's product the booth showcases 
booth_category: Category of the booth - Large, Medium, Small etc. 
booth_type: Type when the booth - Normal, 2D, Immersive etc. 
hidden_booth: Booth which is not published on the platform. Such a booth was created but was not displayed 
allow_registration: Boolean, whether the booth is accepting registration 
boothzoneid: identity of the zone, Booth is associated with which Zone. 
 
Booth Owner Table :
Every booth has one or multiple booth owners. Information related to Booth owners are in this table 

booth_owner_id: ID of the Booth Owner(s) 
booth_id: Booth ID associated with the Booth owner 
account_id: Account ID associated with the Booth Owner. You will find this in the Account table, too. 
createdat_time: Timestamp when the Booth owner ID was created 
createdat_date: Date when the Booth owner ID was created 
updatedat_time: Timestamp when the Booth owner ID was last updated
updated_date: Date when the Booth owner ID was last updated 
event_id: The event associated with the Booth 

Event Table
This is the table where you will find information related to the Events. 

event_id: Event ID 
title: Title of the Event 
description: Description of the Event
start_time: Start time of the Event 
start_date: Start date of the Event
end_time: End time of the Event
end_date: End date of the Event
time_zone: Time zone of the Event
createdat_time: Createdat TIME 
createdat_date: Createdat DATE 
updatedat_time: Updatedat TIME
updatedat_date: Updatedat DATE 
status: Status of the Event 
next_uid: Next UID 
registration_template: Registration TEMPLATE 
lobby_layout_id: Layout ID of the Lobby
color_theme: Color THEME 

Event Location table 
The Event Location table gives us the footprint of the users across different locations 
against the timestamp, which is why you will find multiple appearances of the same 
account id as I move from one zone/ location to another, the information is captured as a 
heartbeat.  

location_id: Location ID
event_name : Event Name associated with the Location
account_id: Account ID of the Users of the event
location: Name of the Location/ zone
created_at:Date & timestamp when the location was crated 
location_ref_id:Location reference ID, which is used for other external mapping Location reference ID, which is used for other external mapping 


Event Role table
This table shows the highest role of a user. 

event_role_id: Event Role ID
event_name: Event name associated with the role
account_mail: email id associated with Account ID, Note that email id is a unique identifier for each user or account ID. That means there is a one-to-one mapping between the account id and account email 
role: The Highest role of the user
status: Status of the user
created_at: Date timestamp when the id was created 
updated_at: Date timestamp when the id was updated 


Segment Table
A stage is where the main event is taking place with speaking, panel discussion etc. These sessions have a specific start and end time, each session is called a Segment. Therefore, a stage is broken into multiple sequential segments, and different sessions are conducted there.  
 
segment_id: Segment ID 
event_id: Segment is associated with this event 
type: Type of the segment, this is always Stage 
ref_id: External reference ID 
title: Title of the Segment 
start_time: Start time of the Segment
start_date: Start date of the Segment
end_time: End time 
end_date: End date
createdat_time: Created time 
Created_date: createdat date 
updatedat_time: Last Updated time 
updated_date: Last updated date 
stage_id: Stage id associated with this segment 
hidden_segment: boolean 1/0 
broadcast_status: Broadcast status 
id_dummy: Boolean, in case its a dummy id 


Segment Speaker Table 
Every segment has one or multiple speakers. 

segment_speaker_id: Segment speaker ID 
createdat_time: Created at time TIME 
createdat_date: Created at date DATE 
updatedat_time: Updated at time TIME
updatedat_date: Updated at date DATE 
segment_id: Segment ID with which this speaker is associated. 


Speaker Table 
This table stores the data of a speaker.  

speaker_id: Speaker ID
event_id: Event ID associated with this speaker
Speaker ID is associated with this Event.  account_id: Account ID of the user. Remember, same account ID may appear in one or multiple events. However, from one ever to another, their speaker ID will be different 
email: Email of the user
company: Company they represent 
headline: Headline/ designation of the speaker
createdat_time: Created at time
createdat_date: Created at date 
updatedat_time: Updated at time 
updatedat_date: Updated at date
ticket_tag_type: Ticket type. 
 

Stage Table 
Stage as one of the zones, stores information related to the stage. 

stage_id: Stage ID
event_id: Event ID 
name: Stage Name 
createdat_time: Created time 
createdat_date: Created date 
updatedat_time: Updated time 
updatedat_date: Updated date 
opensat_time: When the stage opened 
opensat_date: When the stage opened date 
stage_layout: Stage layout 
size: Size of the stage
color: Color of the stage
stage_order: Order of the stage. This is the sequence of the stage 
stage_access: Stage access could for ALL or PRIVATE, in case those are paid or dedicated to specific set of audiences only.
layout_theme: Layout theme of the event 
is_interprefy_support: Boolean values related to support available 
is_caption_support: Boolean values related to support available 
is_recording_support: Boolean values related to support available 
is_dry_run: Is this a dry run? 


Zone Table 
This table shows which zones were created in an event. 
 
zone_id: Zone ID
event_id: Event associated with the Zone 

type: Type of the Zone
start_time: Start time of the Zone

start_date: Start date of the Zone
end_time: End time of the Zone
end_date: End date of the Zone
active: Active zone or not
"""

# Initialize SQLite Database
def init_database(db_path: str) -> SQLDatabase:
    db_uri = f"sqlite:///{db_path}"
    return SQLDatabase.from_uri(db_uri)

def get_sql_chain(db):
    template = f"""
    You are an SQLite3 database expert, highly skilled in writing and optimizing SQL queries for SQLite databases.
    The SQL database contains the following tables and columns:
    <SCHEMA>{{schema}}</SCHEMA>
    Relationships between tables are as follows:

    {BROAD_DESCRIPTION}

    Here is the history of previous questions and their corresponding SQL queries and results: {{chat_history}}

    Please use your expertise to convert English questions into efficient and accurate SQL queries.
    Ensure that you correctly use relationships between tables when needed.
    Please use your expertise to convert English questions into efficient and accurate SQL queries.

    **Instruction** - Generate only the SQL query and nothing else irrespective of the question asked by the user.
    Please use your expertise to convert English questions into efficient and accurate SQL queries.
    
    Consider the following examples for guidance:

    Example 1: How many records are present in the STUDENT table?
    SQL command: SELECT COUNT(*) FROM STUDENT;

    Example 2: List all students studying in the Data Science class.
    SQL command: SELECT * FROM STUDENT WHERE CLASS = 'Data Science';

    Example 3: Retrieve the names of students in Section A.
    SQL command: SELECT NAME FROM STUDENT WHERE SECTION = 'A';

    Example 4: Count the number of students in each class.
    SQL command: SELECT CLASS, COUNT(*) FROM STUDENT GROUP BY CLASS;

    Example 5: Get all details of students sorted by their names.
    SQL command: SELECT * FROM STUDENT ORDER BY NAME;

    Ensure that the generated SQL queries do not include unnecessary formatting characters (such as backticks, triple backticks, or the word "sql").
    Always verify that the generated queries are syntactically correct and optimized for execution in an SQLite environment.

    only return Sqlite query and nothing else irrespective of the question asked by the user.

    Also while generating the query, consider the following:
    - Use the correct table and column names.
    - Use the appropriate SQL keywords and functions.
    - Optimize the query for performance and efficiency.
    - Handle any potential errors or exceptions that may occur during query execution.
    - Ensure that the query results are accurate and relevant to the question asked.
    - Do not generate responses like this: "SQL: SELECT * FROM inventory ORDER BY last_update DESC LIMIT 10;" as the word "SQL" is not required and is not a part of any sql query. only return the query and nothing else.
    - Do not generate responses like this: "SQLite: SELECT * FROM inventory ORDER BY last_update DESC LIMIT 10;" as the word "SQLite" is not required and is not a part of any sql query. only return the query and nothing else.
    - do not include any backticks or triple backticks in the response.
    - Do not include the word "sql" in the response.
    - Do not include any unnecessary formatting characters in the response.
    - Do not include any unnecessary information in the response.
    - your response should not be anything like this"Generated SQL query: Q: Calculate the total sales for each staff member. SQL: SELECT staff_id, SUM(amount) AS total_sales FROM payment GROUP BY staff_id;" 
    as this causes this error :
        The Response is
        An error occurred: near "Q": syntax error

    - In case of complex queries like join operation and complex join operation. Make sure the columns and the tables are correctly used. Thoroughly study the scema before performing the join operation. The join operation should be done correctly and efficiently. Handle the null values appropriately.
    Do not generate anything other than the Query. Do not even mention the word SQL or Q or anything like this in the response and should only be pure SQL query.

    The response should be like this:

    Q -How many people attended the event?

    SELECT COUNT(DISTINCT ( a.account_id )) FROM account AS a JOIN event_role AS er ON a.email = er.account_mail.....; 

    And Not like this:

    Q - How many people attended the event?

    sql SELECT COUNT(DISTINCT ( a.account_id )) FROM account AS a JOIN event_role AS er ON a.email = er.account_mail........; 

    as there exists a redundant keyword 'sql' in the response.

    your turn now:
    Question : {{question}}
    Sql Query:
    """
    prompt = ChatPromptTemplate.from_template(template)
    
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)
    
    def get_schema(_):
        return db.get_table_info()

    return (
        RunnablePassthrough.assign(schema=get_schema)
        | prompt
        | llm
        | StrOutputParser()
    )

def get_response(user_query: str, db: SQLDatabase, chat_history: list) -> str:
    sql_chain = get_sql_chain(db)
    return sql_chain.invoke({
        "question": user_query,
        "chat_history": chat_history
    })

def execute_query(db_path: str, query: str):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    connection.close()
    return results, column_names

# def init_pandasai_agent(data: pd.DataFrame) -> Agent:
#     user_defined_path = f"images/{uuid.uuid4()}"
#     if not os.path.exists("images"):
#         os.makedirs("images")
    
#     model = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)
#     agent = Agent(data, config={"llm": model, "save_charts": True, "save_charts_path": user_defined_path})
    
#     return agent, user_defined_path

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello! I'm your SQL ASSISTANT... How Can I help?"),
    ]

if "generated_query" not in st.session_state:
    st.session_state.generated_query = ""

if "user_defined_path" not in st.session_state:
    st.session_state.user_defined_path = None

load_dotenv()

st.set_page_config(page_title="SQL Assistant")

st.title("Intelligent SQl bot")

with st.sidebar:
    st.subheader("Settings")
    st.write("Enter your database file path:")

    db_path = st.text_input("Database File Path", value="database.sqlite")

    if st.button("Connect"):
        with st.spinner("Connecting to database..."):
            db = init_database(db_path)
            st.session_state.db = db
            st.session_state.db_path = db_path  # Save the database path
            st.success("Connected to database!")

if "db" in st.session_state:
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)

    user_query = st.chat_input("Type a message...")
    if user_query is not None and user_query.strip() != "":
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        with st.chat_message("Human"):
            st.markdown(user_query)

        with st.chat_message("AI"):
            generated_query = get_response(user_query, st.session_state.db, st.session_state.chat_history)
            st.session_state.generated_query = generated_query  # Store the generated query
            
            # Log user input and LLM response
            logging.info(f"User Query: {user_query}")
            logging.info(f"Generated SQL Query: {generated_query}")

            st.markdown(f"SQL Query:\n```sql\n{generated_query}\n```")
        
        st.session_state.chat_history.append(AIMessage(content=f"SQL Query:\n```sql\n{generated_query}\n```"))

    if st.button("Execute Query"):
        with st.spinner("Executing SQL query..."):
            try:
                results, columns = execute_query(st.session_state.db_path, st.session_state.generated_query)
                
                # Log the executed query and result
                logging.info(f"Executed Query: {st.session_state.generated_query}")
                logging.info(f"Query Results: {results}")
                
                if results:
                    
                    df = pd.DataFrame(results, columns=columns)
                    st.dataframe(df)

                    
                    save_path = save_dataframe(df)
                    st.session_state.uploaded_file = save_path 

                else:
                    st.write("No results found.")
                    logging.info("No results found.")
            except sqlite3.OperationalError as e:
                st.write(f"Error: {e}")
                logging.error(f"SQL Execution Error: {e}")
else:
    st.write("Please connect to a database.")

messages = ["Generating...", "Hold on...", "Thinking...", "Loading...", "Processing..."]
# Collapsible section for the main logic
with st.expander("Upload a File and Generate Visualizations"):
    
    # File Upload
    uploaded_file = st.file_uploader(
        "Choose a CSV file", 
        type="csv", 
        key="file", 
        help="Upload a CSV file to get started", 
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        st.write("File uploaded successfully")
        
        try:    
            data = pd.read_csv(uploaded_file, encoding='unicode_escape')
        except Exception as e:
            data = pd.read_csv(uploaded_file)

        st.write(data.head(5))
        st.write("First 5 rows")

        # Create the agent (assuming an Agent class exists)
        agent = Agent(data, config={
            "llm": model, 
            "save_charts": True,
            "save_charts_path": user_defined_path,
        })

        # Text area for user to input a prompt
        prompt = st.text_area("Let's talk with the data:")

        if st.button("Ask"):
            if prompt:
                with st.spinner(random.choice(messages)):
                    st.write(agent.chat(prompt))

        st.header("Visualizations")

        # Display saved visualizations
        try:
            for i in os.listdir(user_defined_path):
                if os.path.isfile(os.path.join(user_defined_path, i)):
                    st.image(os.path.join(user_defined_path, i), use_column_width=True)
        except Exception as e:
            st.write("No visualizations to display")