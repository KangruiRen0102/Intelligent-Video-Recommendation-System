FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# Copy FastAPI code
COPY model/api/app /app

# Install requirements
COPY model/api/requirements.txt ./
RUN pip install -r requirements.txt

# Copy weights^M
COPY model/dataset /dataset
COPY model/checkpoint /checkpoint
