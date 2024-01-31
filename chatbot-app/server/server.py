from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Loading environment variables
load_dotenv()


# Azure credentials and search client setup
service_name = os.getenv('searchservice')
search_key = os.getenv('searchkey')
search_endpoint = f"https://{service_name}.search.windows.net/"
index_name = os.getenv('index')
search_credential = AzureKeyCredential(search_key)

azure_endpoint = os.getenv("azure_endpoint")
azure_key = os.getenv("azure_key")

deployment_id = os.getenv("deployment_id")


KB_FIELDS_CONTENT = os.environ.get("KB_FIELDS_CONTENT") or "content"
KB_FIELDS_CATEGORY = os.environ.get("KB_FIELDS_CATEGORY") or "category"
KB_FIELDS_SOURCEPAGE = os.environ.get("KB_FIELDS_SOURCEPAGE") or "sourcepage"


openai_client = AzureOpenAI(
  azure_endpoint = azure_endpoint, 
  api_key= azure_key,  
  api_version="2023-12-01-preview"
)

search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=index_name,
    credential=search_credential)

def generate_answer(conversation):
    response = openai_client.chat.completions.create(
    model=deployment_id,
    messages=conversation,
    temperature=0,
    max_tokens=1000,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    stop = [' END']
    )
    return (response.choices[0].message.content).strip()

# Define your search logic here
def search_documents(user_input):
    results = search_client.search(
        user_input, 
        filter=None,
        query_language="en-us", 
        query_speller="lexicon", 
        top=3)
    print(f"Raw results {results}")
    return [doc for doc in results]

#class ChatHistory(BaseModel):
#    chatHistory: list[dict[str, str]]

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
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"message": str(exc)})

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    chat_history = body.get('chatHistory')
    print(chat_history)
    
    user_input = chat_history[-1]['content'] if chat_history and chat_history[-1]['role'] == 'user' else None

    if not user_input:
        raise HTTPException(status_code=400, detail="No message provided in the request")

    try:
        # Search documents based on user input
        search_results = search_documents(user_input)
        print(search_results)
        
        if search_results:
            # Prepare the content for OpenAI prompt
            results = [doc[KB_FIELDS_SOURCEPAGE] + ": " + doc[KB_FIELDS_CONTENT].replace("\n", "").replace("\r", "") for doc in search_results]
            content = "\n".join(results)
            #content = "\n".join([doc['content'] for doc in search_results])
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

        return {"reply": reply, "documents": [{"title" : doc[KB_FIELDS_SOURCEPAGE], "content": doc[KB_FIELDS_CONTENT]} for doc in search_results]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
