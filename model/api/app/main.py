from random import sample

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from prometheus_fastapi_instrumentator import Instrumentator

from inference import infer, prepare_model
from helpers import Periodic, store_recommendations, get_model_version


app = FastAPI()
Instrumentator().instrument(app).expose(app)
recommendations = []


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse("user_id must be an integer.", status_code=422)


@app.on_event("startup")
async def startup_event():
    global p, model_version

    # Get current model version
    model_version = get_model_version()

    # Start thread to periodically save recommendations to mongo db
    p = Periodic(store_recommendations, 3, args=[recommendations, model_version])
    p.start()

    # Prepare model to make inferences
    # prepare_model()


@app.on_event("shutdown")
def shutdown_event():
    p.stop()  # Terminate thread


@app.get("/", response_class=PlainTextResponse)
def root_msg():
    return "To use our recommendation service, make a GET request to /recommend/{user_id}."


@app.get("/recommend/{user_id}", response_class=PlainTextResponse)
def recommend(user_id: int):
    # try:
    #     return ",".join(map(str, infer(user_id)))
    # except:
    #     return ",".join(map(str, sample(range(10000), 20)))
    recommendations.append(user_id)
    return ",".join(map(str, sample(range(10000), 20)))


