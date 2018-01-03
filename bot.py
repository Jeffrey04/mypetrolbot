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


def start(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="I'm a bot, please talk to me!")


def send_date(bot, update, result):
    if result:
        dates = result[0].text.split('-')

        if dates[0].strip().isdigit():
            dates[0] = '{}{}'.format(
                dates[0].strip(), ' '.join(
                    dates[1].strip().split(' ')[
                        1:]))

        dates = map(dateparser.parse, dates)

        bot.send_message(
            chat_id=update.message.chat_id,
            text='From {}'.format(' to '.join(map(lambda x: x.__format__('%d/%m/%Y'),
                                                  dates))))


def price_handler(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text='Request received, fetching and parsing')

    response = requests.get('https://hargapetrol.my/',
                            headers={'User-Agent': os.environ.get('BOT_AGENT', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:58.0) Gecko/20100101 Firefox/58.0')})

    send_date(bot, update, CSSSelector('div.starter-template > p.lead b i')
              (lxml.html.fromstring(response.text)))

    for block in CSSSelector('.col-xs-12')(
            lxml.html.fromstring(response.text)):
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Price of {} is RM {} per litre ({} from last week)'.format(
                CSSSelector('div')(block)[1].text.strip(),
                CSSSelector('div')(block)[2].text.strip(),
                CSSSelector('div')(block)[3].text.replace(' ', '')))


def price(bot, update):
    logger.info(update.message.text.upper())
    if ((getattr(update, 'from_user', None) and 'price' in update.message.text.lower())
        or ('price' in update.message.text.lower()
            and '@mypetrolbot' in update.message.text.lower())):
        price_handler(bot, update)


logging.basicConfig(level=logging.INFO & logging.DEBUG & logging.ERROR,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

updater = Updater(token=os.environ.get('BOT_TOKEN', 'TOKEN'))
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('price', price_handler, pass_args=False))
dispatcher.add_handler(MessageHandler(Filters.text, price))

updater.start_polling()
