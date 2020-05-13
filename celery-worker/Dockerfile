FROM python:3.7-alpine

RUN apk --no-cache add curl

ENV CELERY_BROKER_URL redis://redis:6379
ENV CELERY_RESULT_BACKEND redis://redis:6379
ENV C_FORCE_ROOT true

WORKDIR /queue
COPY ./requirements.txt /queue

RUN pip install -r requirements.txt

COPY . /queue

ENTRYPOINT celery -A tasks worker --loglevel=info