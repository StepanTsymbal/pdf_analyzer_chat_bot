import tempfile
from io import StringIO

from fastapi import FastAPI, UploadFile
# from pydantic import BaseModel
# from typing import List
# import sqlite3
import uvicorn
from langchain_community.document_loaders import PyPDFLoader

from database import postgresql_service
from helpers import chat_app_helper
from utils import pdf_service

app = FastAPI()


@app.get("/docs/")
async def get_all_docs():
    documents = postgresql_service.get_all_documents()

    return [{"id": document[0], "uuid": document[1], "name": document[2]} for document in documents]


@app.post("/docs/index")
async def index_doc(file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        # Write the uploaded file content to the temporary file
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    loader = PyPDFLoader(temp_file_path)
    data = loader.load()

    pdf_text = pdf_service.process_data(data)

    chat_app_helper.save_documents_to_dbs(pdf_text, file.filename)

    return 'Ok'


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)