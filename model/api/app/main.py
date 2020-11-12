import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.logger import logger as fastapi_logger
from fastapi.responses import PlainTextResponse
from prometheus_fastapi_instrumentator import Instrumentator

from inference import infer, prepare_model

from random import sample

# Set up logging
gunicorn_error_logger = logging.getLogger("gunicorn.error")
gunicorn_logger = logging.getLogger("gunicorn")
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = gunicorn_error_logger.handlers
fastapi_logger.handlers = gunicorn_error_logger.handlers


app = FastAPI()
Instrumentator().instrument(app).expose(app)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse("user_id must be an integer.", status_code=422)


# Prepare model on API startup
@app.on_event("startup")
async def startup_event():
    prepare_model()


@app.get("/", response_class=PlainTextResponse)
def root_msg():
    return "To use our recommendation service, make a GET request to /recommend/{user_id}."


@app.get("/recommend/{user_id}", response_class=PlainTextResponse)
def recommend(user_id: int):
    try:
        return ",".join(map(str, infer(user_id)))
    except:
        return ",".join(map(str, sample(range(10000), 20)))


if __name__ != "__main__":
    fastapi_logger.setLevel(gunicorn_logger.level)
else:
    fastapi_logger.setLevel(logging.DEBUG)
