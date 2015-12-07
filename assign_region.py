import csv
import us
import zipcode


def get_abbr(state):
	lookup_value = us.states.lookup(unicode(state))
	if lookup_value:
		return lookup_value.abbr
	else:
		return None

def get_region_mapping():
	mapping = {}
	with open('regions.txt', "r+") as inputfile:
		reader = csv.reader(inputfile)

		row_num = 0
		for row in reader:
			region = row[0]
			states = row[1:]			

			state_abbreviations = [get_abbr(x) for x in states]

			for abbreviation, state in zip(state_abbreviations, states):
				mapping[state] = row_num
				mapping[abbreviation] = row_num

			row_num += 1

	mapping[None] = -1

	return mapping

def get_region_from_zip(zip_code, mapping=None):
	if not mapping:
		mapping = get_region_mapping()

	zip_code_object = zipcode.isequal(zip_code)

	return mapping[zip_code_object.state]