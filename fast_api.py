from fastapi import FastAPI, UploadFile, Request
from contextlib import asynccontextmanager
import uvicorn
from slowapi import Limiter
from slowapi.util import get_remote_address

from helpers import fast_api_helper
from models.chat import Chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    fast_api_helper.init()
    yield

# TODO: error handling
app = FastAPI(lifespan=lifespan)
limiter = Limiter(key_func=get_remote_address)

# @app.on_event("startup")
# async def startup_event():
#     fast_api_helper.init()


@app.get("/docs/")
@limiter.limit("60/minute")
async def get_all_docs(request: Request):
    return fast_api_helper.get_all_documents()


@app.post("/docs/index")
@limiter.limit("30/minute")
async def index_doc(file: UploadFile, request: Request):
    await fast_api_helper.index_doc(file)

    return 'Ok'


@app.post("/docs/chat")
@limiter.limit("30/minute")
async def chat(chat: Chat, request: Request):
    # await fast_api_helper.index_doc(file)
    print('CHAT fast_api:', chat)
    response = fast_api_helper.process_question(chat)

    return response


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)