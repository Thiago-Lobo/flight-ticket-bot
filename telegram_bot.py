#!/usr/bin/python

import sys
import os
import re
import json
import time
import traceback
import yaml
import logging
from datetime import datetime, timedelta
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from selenium import webdriver

TELEGRAM_COMMAND_TRACK_FLIGHT_PRICE = 'track_flight'
TRACKING_PERIOD_MINUTES = 1

####################################################
## Flights tracker
####################################################

def track_google_flights_url(url):
	result = []

	try:
		chrome_option = webdriver.ChromeOptions()
		chrome_option.add_argument('--headless')
		chrome_option.add_argument('--disable-gpu')
		driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver", options=chrome_option)

		driver.get(url)
		time.sleep(5)

		date = driver.find_element_by_class_name("gws-flights-form__departure-input").text;
		rows = driver.find_elements_by_class_name("gws-flights-results__collapsed-itinerary");

		for row in rows:
			result.append({
				"price": int(re.sub(r'[^0-9]', r'', row.find_element_by_class_name("gws-flights-results__price").text)),
				"hour": row.find_element_by_class_name("gws-flights-results__times").text,
				"carrier": row.find_element_by_class_name("gws-flights-results__carriers").text.split('\n')[0],
				"duration": row.find_element_by_class_name("gws-flights-results__duration").text,
				"airports": row.find_element_by_class_name("gws-flights-results__airports").text,
				"stops": row.find_element_by_class_name("gws-flights-results__stops").text
			})
	except:
		print(traceback.format_exc())
	finally:
		driver.quit()

	return date, result

def flight_to_string(json_data, date):
	return 'Preco: {0}\nData: {1} - {2}\nAeroportos: {3}\nDuracao: {4} ({5})\nCompanhia: {6}'.format(
		json_data['price'],
		date,
		json_data['hour'],
		json_data['airports'],
		json_data['duration'],
		json_data['stops'],
		json_data['carrier']
	)

def track_google_flights(bot, update, url, price_threshold):
	date, result = track_google_flights_url(url)

	valid_results = [x for x in result if x['price'] < price_threshold]

	if len(valid_results) > 0:
		for flight in valid_results:
			bot.send_message(chat_id=update.message.chat_id, text='Voo barato encontrado!\n\n{0}'.format(flight_to_string(flight, date)))

####################################################
## Handler Callbacks
####################################################

def unknown(update, context):
	context.bot.send_message(chat_id=update.message.chat_id, text='Unknown command.', reply_markup=None)

def track_flight(update, context):
	url = context.args[0]
	price_threshold = int(context.args[1])

	context.job_queue.run_repeating(lambda context: track_google_flights(context.bot, update, url, price_threshold), 10)

	context.bot.send_message(chat_id=update.message.chat_id, text='Now tracking flights in URL "{0}" for prices less than {1}.'.format(url, price_threshold))

####################################################
## Initializers
####################################################

def initialize_logging():
	logging.basicConfig(
			filename='flight_bot.log',
			level=logging.DEBUG,
			format='%(asctime)s.%(msecs)03d [%(name)s] %(levelname)-7s %(funcName)s - %(message)s', 
			datefmt='%Y-%m-%d %H:%M:%S'
	)

def load_configuration_file(path):
	file = open(path, 'r')

	loaded = yaml.load(file, Loader=yaml.FullLoader)

	file.close()

	return loaded

def initialize_bot(configuration):
	updater = Updater(token=configuration['telegram-api-key'], use_context=True)
	dispatcher = updater.dispatcher
	
	dispatcher.add_handler(CommandHandler(TELEGRAM_COMMAND_TRACK_FLIGHT_PRICE, track_flight))
	dispatcher.add_handler(MessageHandler(Filters.command, unknown))
		
	updater.start_polling()
	updater.idle()

def main():
	initialize_logging()
	configuration = load_configuration_file('./bot-config.yml')
	initialize_bot(configuration)

if __name__ == '__main__':
	main()
