FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    tini \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY src/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/backend .

ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD ["python", "app.py"]
