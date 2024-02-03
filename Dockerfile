FROM python:3.10-alpine
LABEL authors="M41den"

RUN mkdir /app
COPY . /app
WORKDIR /app
RUN apk update && apk add git
RUN pip3 install -r /app/requirements.txt
CMD ["python3", "server.py"]