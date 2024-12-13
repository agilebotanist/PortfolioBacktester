FROM python:3.11-buster as builder

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

# RUN --mount=type=cache,target=$POETRY_CACHE_DIR python -m poetry install --without dev --no-root
RUN --mount=type=cache,target=$POETRY_CACHE_DIR python -m poetry install --no-root

FROM python:3.11-slim-buster as runtime


ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY . /app

EXPOSE 8501

ENTRYPOINT  ["streamlit", "run", "./app/Random_Portfolio.py"]