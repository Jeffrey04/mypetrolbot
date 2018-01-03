FROM python:3

ARG BOT_TOKEN
ENV BOT_TOKEN ${BOT_TOKEN:-TOKEN}

RUN pip install python-telegram-bot lxml cssselect requests dateparser \
    && mkdir -p /opt/mypetrolbot

ADD bot.py /opt/mypetrolbot

CMD ["python", "/opt/mypetrolbot/bot.py"]