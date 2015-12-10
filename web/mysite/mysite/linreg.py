import findspark

findspark.init("/home/ubuntu/spark")
#findspark.init()

import pyspark
sc = pyspark.SparkContext(appName="final", pyFiles=["/home/ubuntu/CS205_Final_Project/web/mysite/mysite/linreg.py"])
#sc.setLogLevel('ERROR')

import numpy as np

# from GitHub
def cholesky_solution_linear_regression(x_t_x,x_t_y):    
    L = np.linalg.cholesky(x_t_x)    
    z = np.linalg.solve(L,x_t_y)    
    theta = np.linalg.solve(np.transpose(L),z)
    return theta

#convert the data into (x, y, count) tuples
def process_row(row):
	row_values = row.split(" ")
	value = float(row_values[0])
	features = np.array(row_values[1:] + [1], dtype='float64')
	yield "x", np.outer(features, features)
	yield "y", value * features 
	yield "count", 1

def reduce_rows(row1, row2):
	return row1 + row2

def get_coefficients(file_name="/home/ubuntu/CS205_Final_Project/web/mysitematrix.txt"):

	data = sc.textFile(file_name)

	processed_data = data.flatMap(process_row)

	result_rdd = processed_data.reduceByKey(reduce_rows)
	x_t_x =  result_rdd.lookup("x")[0]
	x_t_y = result_rdd.lookup("y")[0]

	values = []
	for row in data.collect():
		values.append(map(float, row.split(" ")[1:]))

	betas = cholesky_solution_linear_regression(x_t_x, x_t_y)

	return betas
