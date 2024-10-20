from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from langchain_community.document_loaders import JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from huggingface_hub import InferenceClient
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants and config
json_file_path = './industry_data_3.json'
api_token = os.getenv("HF_API_TOKEN") 

# Loading JSON and FAISS on startup
@app.on_event("startup")
async def startup_event():
    global documents, embeddings_model, db, client

    # Load and Split JSON file
    jq_schema = '.[] | {industry_name, document_title, project_description, subfeatures: .subfeatures[] | {sub_feature_name, estimatedHours, hourly_rate}}'
    splitter = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=250)
    loader = JSONLoader(file_path=json_file_path, jq_schema=jq_schema, text_content=False)
    documents = loader.load_and_split(text_splitter=splitter)

    # Load embeddings model
    embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    # Load FAISS vector database
    if not os.path.exists('./models/faiss_index'):
        db = FAISS.from_documents(documents, embeddings_model)
        db.save_local('./models/faiss_index')
    else:
        db = FAISS.load_local('./models/faiss_index', embeddings_model, allow_dangerous_deserialization=True)

    # Step 6: Initialize Hugging Face inference client
    client = InferenceClient(api_key=api_token)

# Pydantic model for input queries
class QueryRequest(BaseModel):
    query: str


# Endpoint for the full question-answering pipeline
@app.post("/qa/")
async def question_answering(query_request: QueryRequest):
    query = query_request.query

    try:
        # Perform similarity search
        embedding_vector = embeddings_model.embed_query(query)
        docs = db.similarity_search_by_vector(embedding_vector)
        context = " ".join([doc.page_content for doc in docs[:2]])

        # Prompt
        template = """Answer the question based only on the following context:
        {context}

        Question: {query}
        """
        
        prompt = PromptTemplate.from_template(template)

        repo_id = "mistralai/Mistral-7B-Instruct-v0.2"

        llm = HuggingFaceEndpoint(
            repo_id=repo_id,
            max_length=128,
            temperature=0.5,
            huggingfacehub_api_token=api_token,
        )
        llm_chain = prompt | llm
        print(llm_chain.invoke({"context": context, "query": query}))

        response = llm_chain.invoke({"context": context, "query": query})

        return {"answer": response}
        

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for health check
@app.get("/health/")
async def health_check():
    return {"status": "ok"}
