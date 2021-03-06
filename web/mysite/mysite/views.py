from django.http import HttpResponse
from django.shortcuts import render

import test_regression
import gen_random
import time
import numpy as np
import os
import datetime
import sys

import findspark

#options for server
findspark.init("/home/ubuntu/spark")
home_dir = "/home/ubuntu/CS205_Final_Project/web/mysite/"

#options for local
#home_dir = ""
#findspark.init()

import pyspark
sc = pyspark.SparkContext(appName="final")

# from GitHub
def cholesky_solution_linear_regression(x_t_x,x_t_y):    
    L = np.linalg.cholesky(x_t_x)    
    z = np.linalg.solve(L,x_t_y)    
    theta = np.linalg.solve(np.transpose(L),z)
    return theta

def get_coefficients(file_name="/home/ubuntu/CS205_Final_Project/web/mysitematrix.txt"):
	#uses Spark to load the text file
	data = sc.textFile(file_name)

	#convert the data into (x, y, count) tuples
	def process_row(row):		
		#the row is of the format: y x1 x2 x3 ...
		row_values = row.split(" ")
		value = float(row_values[0])

		#we append a [1] to serve as a blank variable expressing the intercept
		features = np.array(row_values[1:] + [1], dtype='float64')

		yield "x", np.outer(features, features)
		yield "y", value * features 
		yield "count", 1

	#reduces by combining rows
	def reduce_rows(row1, row2):
		return row1 + row2
	
	#processes each row into x and y groups
	processed_data = data.flatMap(process_row)

	result_rdd = processed_data.reduceByKey(reduce_rows)

	x_t_x =  result_rdd.lookup("x")[0]
	x_t_y = result_rdd.lookup("y")[0]	

	values = []
	for row in data.collect():
		values.append(map(float, row.split(" ")[1:]))

	betas = cholesky_solution_linear_regression(x_t_x, x_t_y)

	return betas
	

def home(request):	
	return render(request, "mysite/overview.html")

def get_data(request):
	rows = int(request.POST.get("rows"))
	cols = int(request.POST.get("columns"))	

	#create a random matrix in the file
	gen_random.gen_random_array(rows, cols, home_dir + "matrix.txt")

	#splits the matrix into training and test data
	test_regression.split_file(home_dir + "matrix.txt", home_dir + "matrix_train.txt", home_dir + "matrix_test.txt")

	start = time.time()
	coefs = get_coefficients(home_dir + "matrix_train.txt")

	#tests the coefs
	predict_buy, predict_sell = test_regression.get_recommended_buys(home_dir + "matrix_test.txt", coefs)
	elapsed = time.time() - start

	#gets the top buys and sells	
	top_buys = sorted(predict_buy, key=lambda x: x["change"], reverse=True)[:50]
	top_sells = sorted(predict_sell, key=lambda x: x["change"], reverse=True)[:50]

	#gets the (simulated) event names for the buys and sells
	event_names = os.listdir(home_dir + "../../snapshots_by_event")
	event_names = [home_dir + "../../snapshots_by_event/" + x for x in event_names if x[-4:]==".txt"]

	top_buys = test_regression.get_events_from_simulation(top_buys, event_names)
	top_sells = test_regression.get_events_from_simulation(top_sells, event_names)

	#resorts (as prices may have been updated with true ticket prices)
	top_buys = sorted(top_buys, key=lambda x: x["change"], reverse=True)
	top_sells = sorted(top_sells, key=lambda x: x["change"], reverse=True)

	response = {}
	response['time'] = elapsed

	response["buy_events"] = top_buys
	response["sell_events"] = top_sells



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


