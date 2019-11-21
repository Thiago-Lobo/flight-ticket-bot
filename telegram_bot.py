#!/usr/bin/python

import sys
import os
import re
import json
import time
import traceback
from datetime import datetime, timedelta
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from selenium import webdriver

API_KEY_FILE = 'telegram_api.key'

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
		driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", chrome_options=chrome_option)

		driver.get(url)
		time.sleep(5)

		date = driver.find_element_by_class_name("gws-flights-form__departure-input").text;
		rows = driver.find_elements_by_class_name("gws-flights-results__collapsed-itinerary");

		for row in rows:
			result.append({
				"price": int(filter(str.isdigit, row.find_element_by_class_name("gws-flights-results__price").text.encode('utf8'))),
				"hour": row.find_element_by_class_name("gws-flights-results__times").text.encode('utf8'),
				"carrier": row.find_element_by_class_name("gws-flights-results__carriers").text.encode('utf8').split('\n')[0],
				"duration": row.find_element_by_class_name("gws-flights-results__duration").text.encode('utf8'),
				"airports": row.find_element_by_class_name("gws-flights-results__airports").text.encode('utf8'),
				"stops": row.find_element_by_class_name("gws-flights-results__stops").text.encode('utf8')
			})

		# driver.save_screenshot('screenshot.png')
	except:
		print traceback.format_exc()
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

def unknown(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text='Unknown command.', reply_markup=None)

def track_flight(bot, update, job_queue, args):
	url = args[0]
	price_threshold = int(args[1])

	job_queue.run_repeating(lambda bot, job: track_google_flights(bot, update, url, price_threshold), 10)

	bot.send_message(chat_id=update.message.chat_id, text='Now tracking flights in URL "{0}" for prices less than {1}.'.format(url, price_threshold))

####################################################
## Initializers
####################################################

def initialize_bot():
	k = open(API_KEY_FILE, 'r')

	updater = Updater(token = k.readlines()[0].strip())
	dispatcher = updater.dispatcher
	queue = updater.job_queue
	
	dispatcher.add_handler(CommandHandler(TELEGRAM_COMMAND_TRACK_FLIGHT_PRICE, track_flight, pass_args=True, pass_job_queue=True))
	dispatcher.add_handler(MessageHandler(Filters.command, unknown))
		
	updater.start_polling()
	updater.idle()

def main():
	initialize_bot()

if __name__ == '__main__':
	main()
