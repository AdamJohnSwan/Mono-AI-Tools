# Use an official Python runtime as a parent image
FROM python:3.12


ENV  POETRY_VERSION=2.1.4 \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=off \
  POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

COPY . .

RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-cache --no-interaction 

RUN chmod +x ./start_all.sh

EXPOSE 8001
EXPOSE 8002
EXPOSE 8003
EXPOSE 8004

CMD ["/app/start_all.sh"]
