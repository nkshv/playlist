FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN git clone https://github.com/nkshv/playlist .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8888

CMD ["python", "src/backend.py"]
