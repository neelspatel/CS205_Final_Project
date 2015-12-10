import gen_random
import numpy as np
import time
import datetime

def split_file(input_file, output_file1, output_file2):
	with open(input_file, "r+") as input_data:
		with open(output_file1, "w+") as output_data1:
			with open(output_file2, "w+") as output_data2:
					row_count = 0
					for row in input_data:
						if row_count % 2 == 0:
							output_data1.write(row)
						else:
							output_data2.write(row)

						row_count += 1

#given an input_file name (with rows of the form price feature1 feature2 ...)
#and a list of coefficients, calculates which rows we expect to go up or down in value
def get_recommended_buys(input_file, coefs):
	predict_buy = []
	predict_sell = []

	with open(input_file, "r+") as input_data:
		for i, row in enumerate(input_data):
			#gets the current value and features from the row
			row_values = row.split(" ")
			value = float(row_values[0])
			features = np.array(row_values[1:] + [1], dtype='float64')

			#predicts the new value based on the current features and coefficients
			predicted_value = np.dot(features, coefs)

			cur_row = {}
			cur_row["predicted_value"] = predicted_value
			cur_row["current_value"] = value
			cur_row["change"] = abs(predicted_value - value)
			cur_row["row_index"] = i

			if predicted_value > value:
				predict_buy.append(cur_row)
			elif predicted_value < value:
				predict_sell.append(cur_row)

	return predict_buy, predict_sell

# get_recommended_buys returns a list of rows by row id. We are using simulated data for this example,
# so we want to display a lookup for an event based on this simulated row. 
# Each row has a row number, so we find the index of that row number in event_list (including a modulo)
# and return the appropriate event
def get_events_from_simulation(rows, event_list):
	for row in rows:
		event_index = row['row_index'] % len(event_list)
		cur_event = event_list[event_index]

		#gets the metadata for the current event
		row['metadata'] = get_event(cur_event)
		
		if row['metadata']['price'] != 0:
			row['change'] = row['metadata']['price'] * row['change']

	return rows

#given an event name, returns the event details
def get_event(event_name):
	metadata = ['event_id', 'last_chance', 'act_primary', 'venue_name', 'eventLocation_facet_str', 'zip']
	
	with open(event_name, "r+") as inputfile:
		metadata_values = inputfile.next().split("\t")
		
		cur_event = {metadata[i]: metadata_values[i] for i in range(len(metadata))}

		#formats the date and time
		cur_time = cur_event['last_chance']
		parsed_time = datetime.datetime.strptime(cur_time, "%Y-%m-%dT%XZ")
		formatted_time = parsed_time.strftime("%a %B %-m %Y, %-I:%M %p")
		cur_event['time'] = formatted_time

		event_data_row = inputfile.next().split("\t")
		price = event_data_row[2]
		cur_event["price"] = float(price)

		cur_event['time'] = formatted_time

		return cur_event

		
