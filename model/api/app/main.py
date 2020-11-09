import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.logger import logger as fastapi_logger
from fastapi.responses import PlainTextResponse

from inference import infer, prepare_model

# Set up logging
gunicorn_error_logger = logging.getLogger("gunicorn.error")
gunicorn_logger = logging.getLogger("gunicorn")
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = gunicorn_error_logger.handlers
fastapi_logger.handlers = gunicorn_error_logger.handlers


app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse("user_id must be an integer.", status_code=422)


# Prepare model on API startup
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
