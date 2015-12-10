import gen_random
import numpy as np
import time

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

def get_recommended_buys(input_file, coefs):
	predict_buy = []
	predict_sell = []
	with open(input_file, "r+") as input_data:
		for row in input_data:
			row_values = row.split(" ")
			value = float(row_values[0])
			features = np.array(row_values[1:] + [1], dtype='float64')

			predicted_value = np.dot(features, coefs)

			if predicted_value > value:
				predict_buy.append(row)
			elif predicted_value < value:
				predict_sell.append(row)					

	return predict_buy, predict_sell