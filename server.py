from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_openai import AzureChatOpenAI
from langchain_community.retrievers.azure_cognitive_search import AzureCognitiveSearchRetriever
from openai import AzureOpenAI
import json
import uvicorn

from config import *

llm = AzureChatOpenAI(
            openai_api_key=openai_api_key,
            azure_endpoint=openai_api_endpoint,
            openai_api_version=openai_api_version,
            deployment_name=deployment_id_gpt)

retriever = AzureCognitiveSearchRetriever(
            service_name=service_name,
            api_key=searchkey,
            **config_azure_retriever)

chain = RetrievalQA.from_chain_type(llm=llm,
                                    retriever=retriever,
                                    **config_QA_chain)

openai_client = AzureOpenAI(
  azure_endpoint = openai_api_endpoint,
  api_key= openai_api_key,
  api_version=openai_api_version
)

def generate_answer(conversation):
    response = openai_client.chat.completions.create(
    model=deployment_id_gpt,
    messages=conversation,
    **config_conversation)
    return (response.choices[0].message.content).strip()

# FastAPI app instance
app = FastAPI()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.exception_handler(Exception)
async def exception_handler(exc: Exception):
    return JSONResponse(status_code=500, content={"message": str(exc)})

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    chat_history = body.get('chatHistory')
    print(chat_history)
    
    user_input = chat_history[-1]['content'] if chat_history and chat_history[-1]['role'] == 'user' else None

    if not user_input:
        raise HTTPException(status_code=400, detail="No message provided in the request")

    #try:
    # Search documents based on user input
    response = chain({"query": user_input})

    if response["source_documents"]:
        # Prepare the content for OpenAI prompt
        results = [json.loads(doc.metadata['metadata'])["source"] + ": " + doc.page_content.replace("\n", "").replace("\r", "") for doc in response["source_documents"]]
        content = "\n".join(results)
    else:
        content = None
    # Generate the conversation format for OpenAI
    conversation = [
        {"role": "system", "content": "Assistant is a great language model that accurately answers questions based on document entries."}] + \
        [message for message in chat_history if message['role'] != 'document'] + \
    ([
        {"role": "assistant", "content": content},
        {"role": "user", "content": user_input}
    ] if content else [{"role": "user", "content": user_input}])
    # Get the answer from OpenAI
    reply = generate_answer(conversation)
    print(reply)
    return {"reply": reply, "documents": [{"title" : json.loads(doc.metadata['metadata'])["source"], "content": doc.page_content} for doc in response["source_documents"]]}

    #except Exception as e:
    #    raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
