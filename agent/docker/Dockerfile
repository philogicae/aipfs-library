ARG PYTHON_VERSION=3.12.7

FROM python:${PYTHON_VERSION}-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements*.txt ./

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libc6-dev && \
    pip install --no-cache-dir --upgrade pip wheel setuptools && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-enforced.txt && \
    apt-get remove -y gcc libc6-dev && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /root/.cache/* /tmp/* && \
    find /usr/local/lib/python3.12/site-packages -name "*.pyc" -delete && \
    find /usr/local/lib/python3.12/site-packages -name "__pycache__" -exec rm -r {} +

FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/usr/local/bin:/usr/local/lib/python3.12/site-packages/playwright/driver:${PATH}"

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

RUN apt-get update && \
    python -m playwright install --with-deps chromium && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 1789

CMD ["python", "-m", "robyn", "src/server.py", "--fast"]