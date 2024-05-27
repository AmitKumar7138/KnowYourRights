## Langchian componet Imports
from langchain_community.vectorstores.cassandra import Cassandra
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain_openai import OpenAI
from langchain_openai import OpenAIEmbeddings

from langchain.text_splitter import CharacterTextSplitter

## Support for dataset retrival with Huggin face
from datasets import load_dataset

## With Cassio the engibne powering tje AstraDB integration in Langcahin
import cassio

from PyPDF2 import PdfReader
from typing_extensions import Concatenate
import os
from dotenv import load_dotenv
import streamlit as st

# Set Streamlit page configuration
st.set_page_config(page_title="Indian Constitution Q&A")

load_dotenv()  #take enviroment variables from .env


llm = OpenAI(openai_api_key = os.getenv("OPENAI_API_KEY"))
embedding = OpenAIEmbeddings(openai_api_key = os.getenv("OPENAI_API_KEY"))


## Intialize connection with Astradb
cassio.init(token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"), database_id=os.getenv("ASTRA_DB_ID"))

astra_vector_store= Cassandra(
    embedding=embedding,
    table_name="consti_qa",
    session=None,
    keyspace=None,
)

astra_vector_index = VectorStoreIndexWrapper(vectorstore=astra_vector_store)


# Define function to get response from vector store index
def get_response(input):
    answer = astra_vector_index.query(input, llm=llm).strip()
    response = f"\"{answer}\"\n"
    return response


# Initialize Streamlit app
st.image("cons.jpeg", caption="Constitution of India", use_column_width=True)

st.header("Ask any question related to the Constitution of India.")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for sender, message in st.session_state.messages:
    if sender == "user":
         st.markdown(f"""
        <div style="background-color:#daf5e9; padding:10px; border-radius:5px; margin-bottom:5px; color:#000">
            <strong>You:</strong> {message}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background-color:#f0f0f5; padding:10px; border-radius:5px; margin-bottom:5px; color:#000">
            <strong>Bot:</strong> {message}
        </div>
        """, unsafe_allow_html=True)

# User input
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("You: ", key="input")
    submit = st.form_submit_button("Send")

# Handle user input
if submit and user_input:
    # Display user message
    st.session_state.messages.append(("user", user_input))
    # Get bot response
    response = get_response(user_input)
    st.session_state.messages.append(("bot", response))
    st.experimental_rerun()
