from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from rag.utils import config_loader
import uvicorn
from rag.blocks.chains import ChainerFromConfig
import subprocess
import time
import webbrowser
from multiprocessing import Process

args, config=config_loader()

assert ("chain" in config), "Your config doesn't have a chain !"

chatbot = ChainerFromConfig(config["chain"]).chain()

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
        return {"reply": reply,
                "documents": [{
                    "title" : doc.metadata['source'],
                    "content": doc.page_content} for doc in response.get("source_documents", [])]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def front(path):

    # Start Angular development server using subprocess
    subprocess.run(['ng', 'serve','--open=true'], shell=True, cwd=path)

def back(port):
    uvicorn.run(app, host="0.0.0.0", port=port)

def main():

    process_back = Process(target=back,args=(config.get("port", 3000),))
    process_front = Process(target=front,args=(config.get("app_path", 'rag/frontend/'),))

    process_back.start()
    process_front.start()

    process_back.join()
    process_front.join()

    if args.verbose:
        print("Your RAG is up and running")


if __name__ == "__main__":
    main()

