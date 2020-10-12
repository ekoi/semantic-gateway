FROM python:3
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$PATH"


RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential \
        git

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
ENV POETRY_VERSION=1.1.2
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

ENV FASTAPI_ENV=development
#ENV FASTAPI_ENV=production

WORKDIR /app

RUN git clone https://github.com/ekoi/semantic-gateway /tmp/semantic-gateway && \
    cp -r /tmp/semantic-gateway/*  /app/ && \
    poetry install --no-dev  # respects

EXPOSE 8205

CMD ["poetry", "run", "uvicorn", "--reload", "--host=0.0.0.0", "--port=8205", "src.main:app"]
