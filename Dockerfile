FROM python:3.13-slim
LABEL authors='calamistratus'

WORKDIR .

RUN apt-get update
RUN apt-get install -y gcc

RUN pip install --upgrade pip
RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-root

COPY . .
ENV PYTHONPATH=./

CMD uvicorn main:app --host 0.0.0.0 --port $PYTHON_PORT