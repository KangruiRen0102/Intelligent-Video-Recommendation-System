from typing import Optional

from fastapi import FastAPI

from .inference import inference_service

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/infer/{user_id}")
def read_item(user_id: int, q: Optional[str] = None):
    return {"movies": inference_service(user_id)}
