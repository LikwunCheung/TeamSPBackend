FROM python:3.7

MAINTAINER lihuanzhang

ENV RUN_MODE=DEPLOY
ENV http_proxy=proxy.unimelb.edu.au:8000
ENV https_proxy=proxy.unimelb.edu.au:8000

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install -y default-mysql-client
RUN mkdir /app
WORKDIR /app/

COPY requirements.txt /app
RUN pip3 install -r requirements.txt

COPY . /app/

EXPOSE 8081

CMD ["python3", "manage.py", "runserver", "0:8081"]
