import os
import csv
import time
import datetime
import pytz

#converts the snapshot to a time
def snapshot_name_to_time(snapshot):
	snapshot_time = datetime.datetime.strptime(snapshot, "snapshot_%m_%d_%Y_%H_%M.json")
	snapshot_time_seconds = time.mktime(snapshot_time.timetuple())

	return snapshot_time_seconds

def time_to_snapshot_name(snapshot_time_seconds):
	snapshot_time = datetime.datetime.fromtimestamp(snapshot_time_seconds)
	snapshot_time_string = snapshot_time.strftime("snapshot_%m_%-d_%Y_%-H_%-M.json") 

	return snapshot_time_string


#converts the snapshot name into a list of
#month, date, year, hour, minute
def snapshot_name_to_list(snapshot):
	snapshot = snapshot.replace("snapshot_", "").replace(".json", "")

	components = snapshot.split("_")
	components = map(int, components)
	return components

def generate_snapshots_between(first, last):
	first_components = snapshot_name_to_list(first)
	last_components = snapshot_name_to_list(last)

	first_date = datetime.datetime(month=first_components[0], day=first_components[1], year=first_components[2])
	last_date = datetime.datetime(month=last_components[0], day=last_components[1], year=last_components[2])

	dates = []

	current_date = first_date
	while current_date <= last_date:
		current_date_string = current_date.strftime("%m_%-d_%Y_")		

		if current_date == first_date:
			#generates times from the start time to 24, in groups of 6
			times = range(first_components[3],24+6,6)
		elif current_date == last_date:
			#generates times from 0 to the end time, in groups of 6
			times = range(0,last_components[3]+6,6)
		else:
			#generates times from 0 to 24, in groups of 6
			times = range(0,24+6,6)

		time_strings = [current_date_string + str(x) + "_0.json" for x in times]

		dates.extend(time_strings)

		current_date += datetime.timedelta(days=1)

	return dates	


snapshots = os.listdir("snapshots_by_event")
snapshots = [x for x in snapshots if x[-4:]==".txt"][:5]

for snapshot in snapshots:	
	with open("snapshots_by_event/"+snapshot, "rb") as inputfile:
		reader = csv.reader(inputfile, delimiter="\t")

		metadata = reader.next()
		results = []
		for row in reader:
			results.append(row)

		snapshot_names = [x[0] for x in results]
		snapshot_times = [snapshot_name_to_time(x) for x in snapshot_names]
		snapshot_names_from_times = [time_to_snapshot_name(x) for x in snapshot_times]
		
		#sanity check for conversions
		assert snapshot_names == snapshot_names_from_times

		min_time = min(snapshot_times)
		max_time = max(snapshot_times)

		min_time_string = time_to_snapshot_name(min_time)
		max_time_string = time_to_snapshot_name(max_time)

		full_snapshot_list = generate_snapshots_between(min_time_string, max_time_string)

		print full_snapshot_list

