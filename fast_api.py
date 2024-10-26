import logging
import os
from datetime import datetime
from fastapi import FastAPI, UploadFile, Request, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from slowapi import Limiter
from slowapi.util import get_remote_address

from helpers import fast_api_helper
from logging_services import seq_service
from models.chat import Chat
import constants.general_constants as constants


UPLOAD_DIRECTORY = constants.UPLOAD_DIRECTORY

@asynccontextmanager
async def lifespan(app: FastAPI):
    fast_api_helper.init()
    seq_service.seq_logger_init()
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
    yield


app = FastAPI(lifespan=lifespan)
limiter = Limiter(key_func=get_remote_address)

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logging.exception(f"Unexpected error occurred: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error. Check logs"},
    )


@app.get("/home/")
@limiter.limit("60/minute")
async def get_chat_gui(request: Request):
    return FileResponse("home.html")


@app.get("/docs/")
@limiter.limit("60/minute")
async def get_all_docs(request: Request):
    return fast_api_helper.get_all_documents()


async def process_and_upload_to_pinecone(file_content, filename, file_path):
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)

    await fast_api_helper.process_and_upload_to_pinecone(file_path=file_path, file_name=filename)


@app.post("/docs/index")
@limiter.limit("30/minute")
async def index_doc(file: UploadFile, request: Request, background_tasks: BackgroundTasks):
    file_content = await file.read()
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)

    background_tasks.add_task(
        process_and_upload_to_pinecone,
        file_content,
        file.filename,
        file_path
    )

    return 'Indexing has been scheduled... ' + str(datetime.now())


@app.post("/docs/chat")
@limiter.limit("30/minute")
async def chat(chat: Chat, request: Request):
    response = fast_api_helper.process_question(chat)

    return response['answer']


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)