FROM python:3.7-alpine

WORKDIR /app
COPY ./requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "120", "app:app"]