ARG PYTHON_VERSION=3.12.7
FROM python:${PYTHON_VERSION}-slim AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update -y && \
    apt-get install gcc -y && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade wheel && \
    pip install --upgrade setuptools && \
    pip install --upgrade pip

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install -r requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements2.txt,target=requirements2.txt \
    pip install -r requirements2.txt

RUN playwright install && playwright install-deps

COPY . .

EXPOSE 1789

CMD robyn src/main.py --fast