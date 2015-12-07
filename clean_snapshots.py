import os
import csv
import time
import datetime
import pytz

from dateutil.relativedelta import relativedelta

SNAPSHOT_DIR = 'snapshots_by_event'
SNAPSHOT_DIR = 'sample_snapshots'
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
    # returns snapshot names
	return dates	

def main():
    snapshots = os.listdir(SNAPSHOT_DIR)
    snapshots = [x for x in snapshots if x[-4:]==".txt"]
    time_series = []
    for snapshot in snapshots:	
        cur_time_series = []
        with open(os.path.join(SNAPSHOT_DIR, snapshot), "rb") as inputfile:
            reader = csv.reader(inputfile, delimiter="\t")
            # we want a dictionary keyed on the names 
            metadata = reader.next()
            # first entry contains data for event
            cur_time_series.append(metadata)
            results = []
            results_dict = {}
            for row in reader:
                results.append(row)
                # strip snapshot_ from results
                results_dict[row[0][9:]] = (row[1], row[2], row[3], row[4])

            # strip snapshot_ from names
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

            # contruct time seriees in order for this event
            prev_price = 0.0
            for sn_i in range(len(full_snapshot_list)):
                sn_key = full_snapshot_list[sn_i]
                if sn_key in results_dict:
                    cur_time_series.append(results_dict[sn_key])
                    # update current min price
                    prev_price = results_dict[sn_key][3]
                else:
                    # use the min price of previous and next
                    def find_next_price(i):
                        if i+1 >= len(full_snapshot_list):
                            return 0.0
                        sn = full_snapshot_list[i+1]
                        while (sn not in results_dict):
                            i += 1
                            if i >= len(full_snapshot_list):
                                return 0.0
                            sn = full_snapshot_list[i]
                        return results_dict[sn][2]
                    try:
                        sn_time = snapshot_name_to_time('snapshot_' + sn_key)
                    except ValueError:
                        #print "Failed on ", sn_key
                        continue 
                    next_price = find_next_price(sn_i) 
                    # we don't care about hte max price, 
                    # maybe we should interpolate the size??
                    cur_time_series.append((sn_time, 0.0, min(prev_price, next_price), None))
            time_series.append(cur_time_series)
            # we also need to figure out what to print out
    good_ts = 0
    good_time_series = []
    for ts in time_series:
        non_zero = False
        has_tix = False
        tix_decreased = False
        last_num_tix = 0
        all_nonzeros = True
        for entry in ts:
            # check if entry is event information (firsst in list) 
            if len(entry) > 5:
                continue 
            if float(entry[2]) > 0:
                non_zero = True
            else:
                all_nonzeros = False

            if entry[3] != None and int(entry[3]) > 0:
                has_tix = True
                if int(entry[3]) < last_num_tix:
                    tix_decreased = True
                last_num_tix = entry[3]    
        if all_nonzeros and non_zero and has_tix and tix_decreased: 
            good_ts += 1
            good_time_series.append(ts)
            print "GOOD ONE FOUND"
            print ts

    # print out good time series: tuples of min price and tix left
    formatted_input = [(ts[0], ts[1:]) for ts in good_time_series]
    print construct_regression(formatted_input) 
    return None

    for event, ts in formatted_input:
        if len(ts) > 8:
            print event
            print ts 

    for ts in good_time_series:
        # where is the metadata for the event
        if len(ts) > 8:
            print [(t[0], t[2], t[3]) for t in ts]
    
    print good_ts, " / ", len(time_series)

def dummy_variable(length, i):
    # return dummy variable with 1 at i
    var = [0] * length
    var[i] = 1
    return var

# need to allow different lags when we print out the data for regression
def construct_regression(event_time_series, lag=5):
    """
    Event time_series is a list of tuples of (evemt, time_series)
    lag is lookback in regression model 
    """
    regression_lines = [] 
    # we want to compute a row of the regression matrix 
    for event, ts in event_time_series:
        # event logic to add in regression coefficients, dummy variables
        # need to figure out region 
        event_regressors = []
        event_date = datetime.datetime.strptime(event[1][:-1], "%Y-%m-%dT%H:%M:%S")
        # iterate through the time series from lag up
        for i in range(lag, len(ts)):
            # look back lag in ts to get regressorrs
            prev_prices =  [e[2] for e in ts[i-lag:i]]
            cur_price = ts[i][2]
            # compute hours until
            cur_date = datetime.date.fromtimestamp(float(ts[i][0]))
            hrs_to_event = relativedelta(event_date, cur_date).hours
            assert(hrs_to_event > 0)
            # dependent variable (current price) goes first
            # append a 1 for the constant term 
            cur_line = [cur_price, 1, hrs_to_event] + event_regressors + prev_prices
            regression_lines.append("\t".join(map(str, cur_line)))
    return regression_lines 

if __name__ == '__main__':
    main()
