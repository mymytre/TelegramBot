import json
import logging
import random
from datetime import datetime
from datetime import time

import requests
import telegram.ext
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def daily_weather(context):
    """" DAILY WEATHER """
    # API KEY
    api_key = "7b8591d0c94f917beca36b15a76c8ad5"
    # krakow location
    lat = "50.05"
    lot = "19.94"
    # url assemble
    base_url = "https://api.openweathermap.org/data/2.5/onecall?"
    final_url = base_url + "lat=" + lat + "&lon=" + lot + '&appid=' + api_key + '&units=metric' + '&lang=ru'
    # api getter
    weather_data = requests.get(final_url).json()
    # weather
    out_string = 'ПОГОДА НА СЕГОДНЯ МЕНЧИКИ!!!\n'
    for i in range(1, 10, 2):
        w_time = weather_data['hourly'][i]['dt']
        w_temp = str(int(weather_data['hourly'][i]['temp']))  # from float to int to string rtd as fck
        w_humidity = str(weather_data['hourly'][i]['humidity'])
        w_info = weather_data['hourly'][i]['weather'][0]['description']
        out_string += datetime.utcfromtimestamp(w_time).strftime(
            '%H:%M') + " --> " + w_temp + '°, ' + w_info + ', влажность --> ' + w_humidity + '\n'

    context.bot.send_message(chat_id='-757860184', text=out_string)


def based_quote(update: Update, context: CallbackContext) -> None:
    """ BAZA """
    update.message.reply_text(get_quote())


def get_quote() -> str:
    """" GET RANDOM QUOTE FROM JSON NAMED quotes.json"""
    with open("quotes.json") as file:
        data = json.load(file)
        return random.choice(data['quotes_list'])


def main() -> None:

    """ Bot setup """
    # token and stuff
    my_token = '5258512499:AAGOzdQh75D2jxtA-tO_6K3j7ui9zqvQmVY'
    updater = telegram.ext.Updater(my_token, use_context=True)
    job_queue = updater.job_queue
    dispatcher = updater.dispatcher

    # quotes
    dispatcher.add_handler(CommandHandler("quote", based_quote))

    # daily weather
    job_queue.run_daily(daily_weather, time(7, 00), days=(0, 1, 2, 3, 4, 5, 6))  # time must be UTC, poland -1 ja jeblan

    # interval version idk
    # job_queue.run_repeating(daily_weather, interval=2.0, first=0.0)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
