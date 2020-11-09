FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# Copy FatAPI code
COPY api/app /app

# Copy datasets and model weights
COPY dataset /dataset
COPY checkpoint /checkpoint

# Install requirements
COPY api/requirements.txt ./
RUN pip install -r requirements.txt

