FROM python:3.11.9-alpine

ARG ENV

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apk update && \
    apk add --virtual build-deps gcc musl-dev && \
    apk add postgresql-dev && \
    apk add netcat-openbsd &&  \
    apk add build-base python3-dev && \
    apk add libffi-dev && \
    apk add git

RUN mkdir /testy
WORKDIR /testy


COPY ./requirements/${ENV}.txt requirements/
RUN pip install -r requirements/${ENV}.txt

COPY . /testy
