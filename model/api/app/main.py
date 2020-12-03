from os.path import join, dirname, abspath
from datetime import datetime
from random import shuffle
import pandas as pd

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from prometheus_fastapi_instrumentator import Instrumentator

from inference import infer, prepare_model
from helpers import Periodic, store_recommendations, get_model_version


ROOT = abspath(join(dirname(__file__), ".."))
DATA = join(ROOT, "dataset", "final_csv")
app = FastAPI()
Instrumentator().instrument(app).expose(app)  # Initialize Prometheus instrumentator
recommendations = []  # Initialize list of recommendations to store to MongoDB
movie_ids = []  # Get all possible web movie ids for fallback recommendation
model_version = None

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse("user_id must be an integer.", status_code=422)


@app.on_event("startup")
async def startup_event():
    global p, model_version, movie_ids

    # Get current model version
    model_version = get_model_version()

    # Start thread to periodically save recommendations to mongo db
    p = Periodic(store_recommendations, 3, args=[recommendations, model_version])
    p.start()

    # Get list of possible movie ids for fallback recommendations
    movie_ids = get_movie_ids()

    # Prepare model to make inferences
    prepare_model()


@app.on_event("shutdown")
def shutdown_event():
    p.stop()  # Terminate thread


@app.get("/", response_class=PlainTextResponse)
def root_msg():
    return (
        "To use our recommendation service, make a GET request to /recommend/{user_id}."
    )


@app.get("/recommend/{user_id}", response_class=PlainTextResponse)
def recommend(user_id: int):
    try:
        user_recommendations = ",".join(map(str, infer(user_id)))
    except:
        shuffle(movie_ids)
        user_recommendations = ",".join(map(str, movie_ids[:10]))
    # Add recommendation to list of recommendations to write to DB
    recommendations.append(
        {
            "timestamp": datetime.now(),
            "user_id": user_id,
            "recommendations": user_recommendations,
            "model_version": model_version,
        }
    )
    return user_recommendations


def get_movie_ids():
    """Return list of all possible web movie ids."""
    df = pd.read_csv(join(DATA, "movies.csv"))
    web_ids = df.web_id.tolist()
    return web_ids
