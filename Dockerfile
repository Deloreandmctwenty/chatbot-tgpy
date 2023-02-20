FROM python:3.9

RUN mkdir /bot
WORKDIR /bot

ENV BOT_TOKEN=BOT:TOKEN

ADD . /bot/
ADD requirements.txt requirements.txt

RUN apt update -y
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "-u", "main.py"]
