import json
import logging
import random
from datetime import datetime
from datetime import time

import requests
import telegram.ext
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# gets api from json
global api_key, my_token, chat_id
with open("data.json") as file:
    from_json = json.load(file)
    my_token = from_json['test_bot_ip']
    api_key = from_json['weather_api']
    chat_id = from_json['channel_id']


def get_weather_from_api():
    """" GET WEATHER FROM API """
    # krakow location
    lat = "50.05"
    lot = "19.94"
    # url assemble
    base_url = "https://api.openweathermap.org/data/2.5/onecall?"
    final_url = base_url + "lat=" + lat + "&lon=" + lot + '&appid=' + api_key + '&units=metric' + '&lang=ru'
    # api getter
    weather_data = requests.get(final_url).json()
    return weather_data


def daily_weather(context):
    context.bot.send_message(chat_id=chat_id, text=daily_weather_generator(0))


def daily_weather_generator(user_option) -> str:
    """
    Generates weather string, works with string_builder
    :param user_option: bassically bool
    if 0 - generates weather for 5 hours with 2 hour interval
    if 1 - generates weather for 5 hours without interval
    :return: printable string for rap bot
    """
    out_string = ''
    if user_option == 0:
        out_string = 'Доброе утро, сигой подогреешь?\n' + string_builder(out_string, user_option)
    elif user_option == 1:
        out_string = 'ПОГОДА НА 5 ЧАСОВ МЕНЧИКИ!!!\n' + string_builder(out_string, user_option)
    return out_string


def string_builder(out_string, user_option) -> str:
    weather_data = get_weather_from_api()
    w_interval = 0
    w_period = 0
    if user_option == 0:
        w_interval = 2
        w_period = 10
    elif user_option == 1:
        w_interval = 1
        w_period = 6

    for i in range(1, w_period, w_interval):
        w_time = weather_data['hourly'][i]['dt']
        w_temp = str(int(weather_data['hourly'][i]['temp']))  # from float to int to string rtd as fck
        w_humidity = str(weather_data['hourly'][i]['humidity'])
        w_info = weather_data['hourly'][i]['weather'][0]['description']
        out_string += datetime.utcfromtimestamp(w_time).strftime(
            '%H:%M') + " --> " + w_temp + '°, ' + w_info + ', влажность --> ' + w_humidity + '\n'
    return out_string


def request_weather(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(daily_weather_generator(1))


def based_quote(update: Update, context: CallbackContext) -> None:
    """ BASED """
    update.message.reply_text(get_quote())


def rap_or_punk(update: Update, context: CallbackContext) -> None:
    """" RAP ?"""
    update.message.reply_text(get_rap())


def start_the_rap(update: Update, context: CallbackContext):
    buttons = [[KeyboardButton("/chto")], [KeyboardButton("/weather")], [KeyboardButton("/quote")]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Припусти штаны, дружище!",
                             reply_markup=ReplyKeyboardMarkup(buttons))


def get_rap() -> str:
    with open("quotes.json") as file:
        data = json.load(file)
        return random.choice(data['rap_or_punk'])


def get_quote() -> str:
    """" GET RANDOM QUOTE FROM JSON NAMED quotes.json"""
    with open("quotes.json") as file:
        data = json.load(file)
        return random.choice(data['quotes_list'])


def main() -> None:
    """ Bot setup """
    # token and stuff
    updater = telegram.ext.Updater(my_token, use_context=True)
    job_queue = updater.job_queue
    dispatcher = updater.dispatcher
    ###
    dispatcher.add_handler(CommandHandler("start", start_the_rap))
    # quotes
    dispatcher.add_handler(CommandHandler("quote", based_quote))
    # weather request
    dispatcher.add_handler(CommandHandler("weather", request_weather))
    # rap or punk
    dispatcher.add_handler(CommandHandler("chto", rap_or_punk))

    # daily weather
    job_queue.run_daily(daily_weather, time(7),  # time must be UTC, poland -1 ja jeblan
                        days=(0, 1, 2, 3, 4, 5, 6))

    # interval version idk
    # job_queue.run_repeating(daily_weather, interval=2.0, first=0.0)

    # waiting
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
