# Parallel Ticket Price Prediction
This code parallelizes linear regression using Spark and OMP/Cython to predict ticket prices. 

## Setup
Our code is written in Python 2.7 and depends on the following modules:
* NumPy
* SciPy
* Cython
* PySpark
* [FindSpark](https://github.com/minrk/findspark)
    * This can be installed with: `pip install git+https://github.com/minrk/findspark.git`

In addition, to run the Cython code, you will need an OMP-compatible C compiler, like the latest version of Clang or GCC.

## Structure
Our code is broken up into a few categories:
* Data processing
    * *process_snapshots.py*  - Transforms data from many snapshot json files to many event time-series files.
    * *clean_snapshots.py* - Iterates over event files and cleans data further. Re-orders any rows out of order, interpolates any missing data, looks up region of the event using *assign_region.py*.
    * *assign_region.py* - Used by *clean_snapshots.py* to look up the region of an event based on its zip code.
    * *sample_snapshots/* - Example data. Each text file is a unique event on StubHub, and contains data on the location of the event, the headlining performer, and the min and max prices, and the number of tickets available for each snapshot.
    * *gen_random.py* - Defines a utility function to create a random matrix and output to a file, with entries delimited by spaces and rows on their own line.
* Parallel linear regression
    * *cholesky.pyx* - Parallel implementation of Cholesky decomposition using OMP/Cython.
    * *pyxbld_omp.py* - Build instructions for *cholesky.pyx*
    * *set_compiler.py* - Compiler instructions for *cholesky.pyx*
    * *linreg.py* - Parallel implementation of linear regression using Spark.
* Testing
    * *test.py* - Functions to test the parallel Cholesky decomposition against NumPy.
    * *test_regression.py* - Times and tests parallel linear regression    * Example data. Each text file is a unique event on StubHub, and contains data on the location of the event, the headlining performer, and the min and max prices, and the number of tickets available for each snapshot.
* Web
    * *web/* - Django site that we used to allow users to interactively train and run a model on simulated data using our parallel implementation of linear regression. Also includes our write-up.

## How to Run
To run a linear regression on a random matrix:
```
import gen_random
import linreg

# create a random 10k x 25 matrix
# this simulates a dataset with 10,000 rows
# the first column in the matrix is the regressand, and the rest are regressors
gen_random.gen_random_array(10000, 25, 'test_matrix.txt')

# run regression on 4 threads
# will return 25 numbers: a constant plus coefficients for the 24 regressors
coefficients = linreg.parallel_get_coefficients(file_name="test_matrix.txt", num_threads=4)
```
