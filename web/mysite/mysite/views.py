from django.http import HttpResponse
from django.shortcuts import render

import test_regression
import gen_random
import linreg
import time
import numpy as np
import os
import datetime

#home_dir = "/home/ubuntu/CS205_Final_Project/web/mysite/"
home_dir = ""

sys.path.append('/home/ubuntu/CS205_Final_Project/web/mysite')


def home(request):	
	return render(request, "mysite/index.html")

def get_data(request):
	rows = int(request.POST.get("rows"))
	cols = int(request.POST.get("columns"))	

	#create a random matrix in the file
	gen_random.gen_random_array(rows, cols, home_dir + "matrix.txt")

	#splits the matrix into training and test data
	test_regression.split_file(home_dir + "matrix.txt", home_dir + "matrix_train.txt", home_dir + "matrix_test.txt")

	start = time.time()
	coefs = linreg.get_coefficients(home_dir + "matrix_train.txt")

	#tests the coefs
	predict_buy, predict_sell = test_regression.get_recommended_buys(home_dir + "matrix_test.txt", coefs)
	predict_buy_events = []
	predict_sell_events = []


	elapsed = time.time() - start

	response = {}
	response['time'] = elapsed

	'''
	#read random data for each of the rows	
	files = os.listdir("../../snapshots_by_event")
	files = ["../../snapshots_by_event/" + x for x in files if x[-4:]==".txt"]

	#gets metadata
	#metadata = ['event_id', 'last_chance', 'act_primary', 'venue_name', 'eventLocation_facet_str', 'zip']
	for i in range(len(predict_buy[:50])):
		cur_file = np.random.choice(files)
		with open(cur_file, "r+") as inputfile:
			metadata = inputfile.next().split("\t")
			predict_buy_events.append(metadata)

	for i in range(len(predict_sell[:50])):
		cur_file = np.random.choice(files)
		with open(cur_file, "r+") as inputfile:
			metadata = inputfile.next().split("\t")
			predict_sell_events.append(metadata)

	response["buy_events"] = predict_buy_events
	response["sell_events"] = predict_sell_events

	#gets the times, in index 1
	for x in response["buy_events"]:
		cur_time = x[1]		
		parsed_time = datetime.datetime.strptime(cur_time, "%Y-%m-%dT%XZ")
		formatted_time = parsed_time.strftime("%c")
		x[1] = formatted_time

	for x in response["sell_events"]:
		cur_time = x[1]		
		parsed_time = datetime.datetime.strptime(cur_time, "%Y-%m-%dT%XZ")
		formatted_time = parsed_time.strftime("%c")
		x[1] = formatted_time

	'''

	#return HttpResponse(json.dumps(response), content_type="application/json")
	return render(request, "mysite/events.html", response)


