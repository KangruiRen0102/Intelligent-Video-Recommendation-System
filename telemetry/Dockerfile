FROM python:3.7.9
RUN apt-get update -y && apt-get install -y build-essential
RUN pip3 install pymongo
RUN pip3 install kafka-python
COPY telemetry.py /app/telemetry.py
COPY config.txt /app/config.txt
COPY config_reader.py /app/config_reader.py
COPY ctr_handlers.py /app/ctr_handlers.py
COPY parsers.py /app/parsers.py
COPY log_handlers.py /app/log_handlers.py
CMD ["python", "/app/telemetry.py"]
