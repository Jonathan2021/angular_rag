from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain.chains import  ConversationalRetrievalChain
from rag.utils import load_configuration
import json
import uvicorn
import argparse
from dotenv import load_dotenv
import os
from rag.blocks.chains import ChainerFromConfig

chatbot = None

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

    try:
        # Search documents based on user input and history
        QandAs=[(message['question'],message['content']) for message in chat_history if message['role'] == 'assistant']
        print(QandAs)
        response = chatbot({"question": user_input,'chat_history':QandAs})

        # Get the answer
        reply = response['answer']
        print(response)
        print(reply)
        return {"reply": reply,
                "documents": [{
                    "title" : doc.metadata.get("source", "No source in metadata"),
                    "content": doc.page_content} for doc in response.get("source_documents", [])]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    global chatbot
    
    parser = argparse.ArgumentParser(description="Process a configuration for the server.")
    parser.add_argument("--config", required=True, help="Path to the configuration file.")
    parser.add_argument("--verbose", action="store_true", default=False, help="Enable verbose mode.")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        raise FileNotFoundError(f"The configuration file {args.config} does not exist.")

    config = load_configuration(args.config)

    if "env_path" in config:
        load_dotenv(dotenv_path=config["env_path"])

    if args.verbose:
        print("Loaded config")        
    
    assert ("chain" in config), "Your config doesn't have a chain !"
    
    chatbot = ChainerFromConfig(config["chain"]).chain()
    
    uvicorn.run(app, host="0.0.0.0", port=config.get("port", 3000))
    
    if args.verbose:
        print("Your RAG is up and running")

if __name__ == "__main__":
    main()