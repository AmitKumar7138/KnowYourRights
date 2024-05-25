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
    response = f"ANSWER: \"{answer}\"\n"
    return response


# Initialize Streamlit app
# st.set_page_config(page_title="Indian Constitution Q&A")
st.header("Ask any question related to the Constitution of India.")

input = st.text_input("Input: ", key="input")

submit = st.button("Ask a question")

if submit:
    response = get_response(input)
    st.subheader("The Response is")
    st.write(response)