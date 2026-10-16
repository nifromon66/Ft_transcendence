FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    tini \
    libmagic1 \
    build-essential \
    libpq-dev \
    libffi-dev \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY src/backend/requirements.txt .

ARG BACKEND_MAC_ARM="false"

RUN if [ "$BACKEND_MAC_ARM" = "true" ]; then \
        export RUSTFLAGS="-C target-cpu=generic" \
        && pip install --no-cache-dir --no-binary=cryptography,cffi -r requirements.txt; \
    else \
        pip install --no-cache-dir -r requirements.txt; \
    fi

COPY src/backend .

ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD ["python", "app.py"]
