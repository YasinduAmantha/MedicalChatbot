from flask import Flask, render_template, jsonify, request
from src.helper import download_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.prompt import *
import os
from transformers import pipeline
from langchain.llms import HuggingFacePipeline

# initialize app.py
app = Flask(__name__)


# load environmental variables
load_dotenv()

PINECONE_API_KEY=os.environ.get('PINECONE_API_KEY')
GOOGLE_API_KEY=os.environ.get('GOOGLE_API_KEY')
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# load existing pinecone index file
embedding = download_embeddings()
index_name = "railway-rules-new"
docserach = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embedding
)

# now create the chain
retriever = docserach.as_retriever(search_type="similarity", search_kwargs={"k":3})
# generator = pipeline("text2text-generation", model="google/flan-t5-base")
# llm = HuggingFacePipeline(pipeline=generator)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}")
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# create basic default route
@app.route("/")
def index():
    return render_template('chatRailway.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    print(input)
    response = rag_chain.invoke({"input": msg})
    print("Response : ", response["answer"])
    return str(response["answer"])


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
