FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# Copy FastAPI code
COPY app /app

# Install requirements
COPY api/requirements.txt ./
RUN pip install -r requirements.txt

