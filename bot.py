from telegram.ext import Updater
from telegram.ext import CommandHandler
from lxml.cssselect import CSSSelector
from lxml.etree import tostring
from telegram.ext import MessageHandler, Filters, InlineQueryHandler
import logging
import requests
import lxml.html
import os
import dateparser

logging.basicConfig(
    level=logging.INFO & logging.DEBUG & logging.ERROR,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)


def start(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=
        "The upstream usually updates the price after 6PM every Wednesday. Issue /price command to fetch the latest price."
    )


def send_date(bot, update, result):
    if result:
        dates = result[0].text.split('-')

        if dates[0].strip().isdigit():
            dates[0] = '{}{}'.format(dates[0].strip(),
                                     ' '.join(dates[1].strip().split(' ')[1:]))

        dates = map(dateparser.parse, dates)

        bot.send_message(
            chat_id=update.message.chat_id,
            text='From {}'.format(
                ' to '.join(map(lambda x: x.__format__('%d/%m/%Y'), dates))))


def price_handler(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Request received, fetching and parsing')

    response = requests.get(
        'https://hargapetrol.my/',
        headers={
            'User-Agent':
            os.environ.get(
                'BOT_AGENT',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:58.0) Gecko/20100101 Firefox/58.0'
            )
        })

    send_date(context.bot, update,
              CSSSelector('div.starter-template > p.lead b i')(
                  lxml.html.fromstring(response.text)))

    for block in CSSSelector('div[itemprop=priceComponent]')(
            lxml.html.fromstring(response.text))[:3]:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Price of {} is RM {} per litre ({} from last week)'.format(
                CSSSelector('div')(block)[1].text.strip(),
                CSSSelector('span[itemprop=price]')(block)[0].text.strip(),
                CSSSelector('div')(block)[3].text.replace(' ', '')))


def price(update, context):
    logger.info(update.message.text.upper())

    if ((getattr(update, 'from_user', None)
         and 'price' in update.message.text.lower())
            or ('price' in update.message.text.lower()
                and '@mypetrolbot' in update.message.text.lower())):
        price_handler(update, context)


def main():
    updater = Updater(token=os.environ.get('BOT_TOKEN', 'TOKEN'), request_kwargs={'read_timeout': 6, 'connect_timeout': 7})
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('price', price_handler, pass_args=False))
    dispatcher.add_handler(MessageHandler(Filters.text, price))

    updater.start_webhook(
        listen='0.0.0.0',
        webhook_url=
            f"{os.environ.get('WEBHOOK_URL','coolsilon.com')}"
            f"{os.environ.get('URL_PATH', '/')}",
        url_path=os.environ.get('URL_PATH', '/'))

class MockBot(object):
    def send_message(self, **kwargs):
        logger.debug(kwargs['text'])

class MockMessage(object):
    chat_id = None

class MockUpdate(object):
    message = MockMessage()


if __name__ == '__main__':
    if os.environ.get('BOT_TOKEN', False):
        main()
    else:
        price_handler(MockBot(), MockUpdate())
