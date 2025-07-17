FROM python:3.12-alpine3.20

ENV PYTHONBUFFERED 1

RUN ln -sf /usr/share/zoneinfo/Europe/Kyiv /etc/localtime
WORKDIR /app

COPY Pipfile Pipfile.lock pyproject.toml ./
RUN python -m pip install --upgrade pip && pip install pipenv
RUN pipenv install --dev --system --deploy

COPY src/* ./