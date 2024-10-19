#-------------------------------------
# STEP 1: Load and Split the JSON File
#-------------------------------------

from langchain_community.document_loaders import JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path

# Define the updated jq schema
jq_schema = '.[] | {industry_name, document_title, project_description, subfeatures: .subfeatures[] | {sub_feature_name, estimatedHours, hourly_rate}}'

# Define file path
json_file_path = './industry_data_3.json'

# Create a text splitter (you can adjust chunk size and overlap based on your needs)
splitter = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=250)

# Initialize JSONLoader
loader = JSONLoader(
    file_path=json_file_path,
    jq_schema=jq_schema,
    text_content=False  # If you want to handle as text later
)

# Use the load_and_split method to load the data and automatically split the content into smaller chunks
documents = loader.load_and_split(text_splitter=splitter)

# Print to check the loaded and split documents
for doc in documents[:3]:  # Limiting to first 3 for brevity
    print(doc)


#-------------------------------------
# STEP 2: Generate Embeddings using Hugging Face
#-------------------------------------

from langchain_huggingface import HuggingFaceEmbeddings

embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

embeddings = embeddings_model.embed_documents(doc.page_content)
print(len(embeddings), len(embeddings[0]))
# print(f"Embedding for document: {embeddings[:3]}...")  # Print the first few dimensions of the embedding for brevity



#-------------------------------------
# STEP 3: Saving and Loading the FAISS Index
#-------------------------------------

from langchain_community.vectorstores import FAISS

db = FAISS.from_documents(documents, embeddings_model)


#-------------------------------------
# STEP 4: Perform a Similarity Search
#-------------------------------------\
    
query = "How many hours will the push notification feature will take?"

embedding_vector = embeddings_model.embed_query(query)
# print("Embedded query: ", embedding_vector[:5])
docs = db.similarity_search_by_vector(embedding_vector)
print("In similarity doc: ", docs[0].page_content)


#-------------------------------------
# STEP 5: Implement the Retriever
#-------------------------------------

retriever = db.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 3}
    # search_kwargs={"score_threshold": 0.5}
)

docs = retriever.invoke(query)
print("Length of retrieved docs: ", len(docs))
print(docs)

#-------------------------------------
# STEP 6: Using the Retrieved Documents with a Language Model (Optional)
#-------------------------------------
import requests
import time
from huggingface_hub import InferenceClient


api_token = "your key"
client = InferenceClient(api_key=api_token)
"""
# Set the headers for authorization
headers = {
    "Authorization": f"Bearer {api_token}"
}

# Choose a model from Hugging Face for question-answering
api_url = "https://api-inference.huggingface.co/models/distilbert-base-uncased-distilled-squad"
# api_url = "https://api-inference.huggingface.co/models/google/flan-t5-base"
"""
# Prepare the context (combine the retrieved document contents)
context = " ".join([doc.page_content for doc in docs])

# Prepare the payload with the question and context
messages = [{"role": "user", "content": f"{query}. Don't mention about the provided context. \n\nContext: {context}"}]

# Call the Phi-3-mini-4k-instruct model using the client.chat_completion method
for message in client.chat_completion(
    model="microsoft/Phi-3-mini-4k-instruct",
    messages=messages,
    max_tokens=500,
    stream=True
):
    # Stream the response from the model
    print(message.choices[0].delta.content, end="")
    
# Define the payload for the Hugging Face API
# payload = {
#     "inputs": {
#         "question": query,
#         "context": context
#     }
# }

"""
# Retry mechanism for handling 503 errors
max_retries = 5
retries = 0
success = False

while retries < max_retries and not success:
    response = requests.post(api_url, headers=headers, json=payload)
    
    if response.status_code == 200:
        # Successfully received response
        result = response.json()
        print("Answer:", result['answer'])
        success = True
    elif response.status_code == 503:
        # Model is still loading, retry after a delay
        print(f"Error 503: Model is still loading. Retrying in 20 seconds... (Attempt {retries + 1} of {max_retries})")
        retries += 1
        time.sleep(20)  # Wait for 20 seconds before retrying
    else:
        # Other error occurred
        print(f"Error {response.status_code}: {response.text}")
        break

# If still unsuccessful after max retries
if not success:
    print("Failed to get a response after several attempts.")

# Make the request to Hugging Face's Inference API
response = requests.post(api_url, headers=headers, json=payload)

# Parse the response from Hugging Face API
if response.status_code == 200:
    result = response.json()
    print("Answer:", result['answer'])
else:
    print("Error:", response.status_code, response.text)
"""
    