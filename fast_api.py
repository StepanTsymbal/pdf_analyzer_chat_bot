import asyncio
import os

from fastapi import FastAPI, UploadFile, Request, HTTPException
from contextlib import asynccontextmanager
import uvicorn
from slowapi import Limiter
from slowapi.util import get_remote_address

from helpers import fast_api_helper
from logging_services import seq_service
from models.chat import Chat

UPLOAD_DIRECTORY = "temp_uploads"


@asynccontextmanager
async def lifespan(app: FastAPI):
    fast_api_helper.init()
    seq_service.seq_logger_init()
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
    yield


app = FastAPI(lifespan=lifespan)
limiter = Limiter(key_func=get_remote_address)


@app.get("/docs/")
@limiter.limit("60/minute")
async def get_all_docs(request: Request):
    try:
        return fast_api_helper.get_all_documents()
    except Exception:
        raise HTTPException(status_code=500, detail='Smth went wrong! Check logs')


@app.post("/docs/index")
@limiter.limit("30/minute")
async def index_doc(file: UploadFile, request: Request):
    try:
        # await fast_api_helper.index_doc(file)
        # return 'Ok'

        file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        await asyncio.create_task(fast_api_helper.process_and_upload_to_pinecone(file_path, file.filename))

        return 'Ok'
    except Exception:
        raise HTTPException(status_code=500, detail='Smth went wrong! Check logs')


@app.post("/docs/chat")
@limiter.limit("30/minute")
async def chat(chat: Chat, request: Request):
    try:
        response = fast_api_helper.process_question(chat)

        return response['answer']
    except Exception:
        raise HTTPException(status_code=500, detail='Smth went wrong! Check logs')


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)