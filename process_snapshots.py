import ijson
import json
import decimal
import os
import unicodecsv as csv
import time
import datetime

def clean_text(text):
	if isinstance(text, str):
		return text.replace("\t", " ").replace("\n", " ").replace("\r", " ")
	else:
		return text

# iterate through the snapshots directory
snapshots = os.listdir("snapshots")
snapshots = [x for x in snapshots if x[-5:]==".json"]

last_index = snapshots.index("snapshot_11_19_2015_6_0.json")
snapshots = snapshots[last_index:]

# create the output directory if necessary
if not os.path.exists("snapshots_by_event"):
	os.mkdir("snapshots_by_event")

for snapshot in snapshots:
	print snapshot

	snapshot_time = datetime.datetime.strptime(snapshot, "snapshot_%m_%d_%Y_%H_%M.json")
	snapshot_time_string = time.mktime(snapshot_time.timetuple())

	inputfile = open("snapshots/"+snapshot)
	objects = ijson.items(inputfile, 'item')	

	variables = ['event_id', 'last_chance', 'act_primary', 'venue_name', 'eventLocation_facet_str', 'zip']
	daily_variables = ['minPrice', 'maxPrice', 'totalTickets']

	object_count = 0

	for cur_object in objects:		
		object_count += 1

		if object_count % 1000 == 0:
			print "\t", object_count

		has_all_variables = True

		#make sure all variables are present
		for variable in variables:
			if variable not in cur_object:
				has_all_variables = False				

		if has_all_variables:
			event_id = cur_object['event_id']			

			#if a file for this event doesn't exist, create one with the appropriate information
			if not os.path.isfile("snapshots_by_event/" + event_id + ".txt"):												
				with open("snapshots_by_event/" + event_id + ".txt", "w+") as outputfile:					
					writer = csv.writer(outputfile, delimiter="\t")
					variable_values = map(clean_text, [cur_object[x] for x in variables])
					writer.writerow(variable_values)

			#write the current information to this file
			with open("snapshots_by_event/" + event_id + ".txt", "a") as outputfile:
				writer = csv.writer(outputfile, delimiter="\t")
				daily_variable_values = map(clean_text, [snapshot, snapshot_time_string] + [cur_object[x] for x in daily_variables])
				writer.writerow(daily_variable_values)

