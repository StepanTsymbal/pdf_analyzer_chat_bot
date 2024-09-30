from fastapi import FastAPI, UploadFile
import uvicorn

from helpers import fast_api_helper

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    # TODO: move to lifespan?
    fast_api_helper.init()


@app.get("/docs/")
async def get_all_docs():
    return fast_api_helper.get_all_documents()


@app.post("/docs/index")
async def index_doc(file: UploadFile):
    await fast_api_helper.index_doc(file)

    return 'Ok'


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)