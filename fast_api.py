import logging
import os
from datetime import datetime
import shutil
import uuid

from fastapi import FastAPI, File, UploadFile, Request, HTTPException, BackgroundTasks
from contextlib import asynccontextmanager
import uvicorn
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel

from helpers import fast_api_helper
from logging_services import seq_service
from models.chat import Chat

UPLOAD_DIRECTORY = "temp_uploads"


@asynccontextmanager
async def lifespan(app: FastAPI):
    fast_api_helper.init()
    # with this line uncommented, API works slower??
    # seq_service.seq_logger_init()
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
    yield


app = FastAPI(lifespan=lifespan)
limiter = Limiter(key_func=get_remote_address)

upload_status = {}


class UploadStart(BaseModel):
    filename: str
    total_size: int


@app.get("/docs/")
@limiter.limit("60/minute")
async def get_all_docs(request: Request):
    try:
        return fast_api_helper.get_all_documents()
    except Exception as ex:
        logging.exception(f'fast_api.py:: docs error: {ex}')
        raise HTTPException(status_code=500, detail='Smth went wrong! Check logs')


async def process_and_upload_to_pinecone(file_content, filename, file_path):
    with open(file_path, "wb") as buffer:
        # content = await file.read()
        buffer.write(file_content)

    await fast_api_helper.process_and_upload_to_pinecone(file_path=file_path, file_name=filename)


@app.post("/docs/index")
@limiter.limit("30/minute")
async def index_doc(file: UploadFile, request: Request, background_tasks: BackgroundTasks):
    try:
        # await fast_api_helper.index_doc(file)
        # return 'Ok'

        file_content = await file.read()

        file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
        # with open(file_path, "wb") as buffer:
        #     content = await file.read()
        #     buffer.write(content)

        # await asyncio.create_task(fast_api_helper.process_and_upload_to_pinecone(file_path, file.filename))
        background_tasks.add_task(
            process_and_upload_to_pinecone,
            file_content,
            file.filename,
            file_path
        )

        return 'Processing... ' + str(datetime.now())
    except Exception as ex:
        logging.exception(f'fast_api.py:: docs/index error: {ex}')
        raise HTTPException(status_code=500, detail='Smth went wrong! Check logs')


@app.post("/docs/chat")
@limiter.limit("30/minute")
async def chat(chat: Chat, request: Request):
    try:
        response = fast_api_helper.process_question(chat)

        return response['answer']
    except Exception as ex:
        logging.exception(f'fast_api.py:: docs/chat error: {ex}')
        raise HTTPException(status_code=500, detail='Smth went wrong! Check logs')


@app.post("/upload/start")
@limiter.limit("30/minute")
async def start_upload(upload_info: UploadStart, request: Request):
    # Generate upload ID
    upload_id = str(uuid.uuid4())

    # Create temporary directory for chunks if it doesn't exist
    os.makedirs("temp_uploads", exist_ok=True)
    os.makedirs(f"temp_uploads/{upload_id}", exist_ok=True)

    # Initialize upload status
    upload_status[upload_id] = {
        "filename": upload_info.filename,
        "total_size": upload_info.total_size,
        "uploaded_size": 0,
        "status": "initiated"
    }

    return {"upload_id": upload_id}


@app.post("/upload/chunk/{upload_id}")
@limiter.limit("600/minute")
async def upload_chunk(upload_id: str, chunk_number: int, request: Request, file: UploadFile = File(...)):
    if upload_id not in upload_status:
        raise HTTPException(status_code=404, detail="Upload ID not found")

    try:
        # Save chunk to temporary file
        chunk_path = f"temp_uploads/{upload_id}/chunk_{chunk_number}"
        with open(chunk_path, "wb") as chunk_file:
            content = await file.read()
            chunk_file.write(content)

        # Update uploaded size
        upload_status[upload_id]["uploaded_size"] += len(content)

        return {
            "chunk_number": chunk_number,
            "uploaded_size": upload_status[upload_id]["uploaded_size"],
            "total_size": upload_status[upload_id]["total_size"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload/complete/{upload_id}")
@limiter.limit("30/minute")
async def complete_upload(upload_id: str, bg_task: BackgroundTasks, request: Request):
    if upload_id not in upload_status:
        raise HTTPException(status_code=404, detail="Upload ID not found")

    try:
        # Combine all chunks
        final_path = f"uploads/{upload_status[upload_id]['filename']}"
        os.makedirs("uploads", exist_ok=True)

        with open(final_path, "wb") as final_file:
            chunk_files = sorted(os.listdir(f"temp_uploads/{upload_id}"),
                                 key=lambda x: int(x.split('_')[1]))

            for chunk_file in chunk_files:
                chunk_path = f"temp_uploads/{upload_id}/{chunk_file}"
                with open(chunk_path, "rb") as chunk:
                    shutil.copyfileobj(chunk, final_file)

        bg_task.add_task(fast_api_helper.process_and_upload_to_pinecone, final_path, upload_status[upload_id]['filename'], upload_id)

        # Clean up
        shutil.rmtree(f"temp_uploads/{upload_id}")
        upload_status[upload_id]["status"] = "completed"

        return {"status": "completed", "filename": upload_status[upload_id]['filename']}

    except Exception as e:
        upload_status[upload_id]["status"] = "failed"
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)