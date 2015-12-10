import gen_random
import linreg
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

def test_parallel(rows, cols, num_threads):
    """
    returns time of linear regression using parallel choelsky 
    """
    gen_random.gen_random_array(rows, cols, "parallel_matrix.txt")
    split_file("parallel_matrix.txt", "parallel_matrix_train.txt", "parallel_matrix_test.txt")
    start = time.time()
    coefs = linreg.parallel_get_coefficients(file_name="parallel_matrix_train.txt", num_threads=num_threads)
    reg_time = time.time() - start
    # return time in seconds of lin reg
    return reg_time

def test():
	#create a random matrix in the file
    gen_random.gen_random_array(1000000, 25, "matrix.txt")

	#splits the matrix into training and test data
    split_file("matrix.txt", "matrix_train.txt", "matrix_test.txt")
    start = time.time()
    coefs = linreg.get_coefficients("matrix_train.txt")
    predict_buy, predict_sell = get_recommended_buys("matrix_test.txt", coefs)
    print time.time() - start

print "About to test parallel cholesky"
rows, cols, num_threads = 10000, 2000, 4
runtime = test_parallel(rows, cols, num_threads)
print "Rows: ", rows, " Cols: ", cols, " Threads: ", num_threads
print "Time: ", runtime

