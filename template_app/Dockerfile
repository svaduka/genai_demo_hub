FROM python:3.12 AS build

WORKDIR /app

COPY --from=libs-python . libs/python/

ENV DO_NOT_TRACK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1 \
    VENV_HOME=/app/.venv

RUN python3 -m venv $VENV_HOME && \
    $VENV_HOME/bin/pip install -U pip setuptools


FROM python:3.12-slim

ENV DO_NOT_TRACK=1

WORKDIR /app

COPY --from=build /app/.venv .venv

COPY app .
COPY entrypoint.sh .
COPY demo_hub.env .env
COPY static/style.css static/style.css

CMD [ "./entrypoint.sh" ]
