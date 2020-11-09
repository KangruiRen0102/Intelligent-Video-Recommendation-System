from fastapi import FastAPI

from inference import infer, prepare_model

from fastapi.responses import PlainTextResponse


import logging
from fastapi.logger import logger as fastapi_logger

gunicorn_error_logger = logging.getLogger("gunicorn.error")
gunicorn_logger = logging.getLogger("gunicorn")
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = gunicorn_error_logger.handlers
fastapi_logger.handlers = gunicorn_error_logger.handlers


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    prepare_model()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/recommend/{user_id}", response_class=PlainTextResponse)
def read_item(user_id: int):
    return ",".join(map(str, infer(user_id)))


if __name__ != "__main__":
    fastapi_logger.setLevel(gunicorn_logger.level)
else:
    fastapi_logger.setLevel(logging.DEBUG)
