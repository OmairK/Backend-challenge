FROM python:3.6.9-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

RUN apk update \
	&& apk add postgresql-dev gcc python3-dev musl-dev
RUN apk update && apk add bash
RUN mkdir /code

WORKDIR /code

COPY requirements.txt /code/

RUN pip install -r requirements.txt
RUN mkdir /code/data
RUN mkdir /code/exports

COPY . /code/

CMD [ "redis-server" ]