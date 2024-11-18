# i have containerized maybe one application in my life... here goes nothing.

FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir flask

EXPOSE 5000

CMD ["python", "processor.py"]
