from fastapi import FastAPI, UploadFile, Request
from contextlib import asynccontextmanager
import uvicorn
from slowapi import Limiter
from slowapi.util import get_remote_address

from helpers import fast_api_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    fast_api_helper.init()
    yield


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


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)