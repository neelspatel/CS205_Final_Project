from scipy.stats import linregress
import numpy as np
import time

import pyximport
pyximport.install(setup_args={"include_dirs":np.get_include()})
import cholesky 


def test_time():
    start = time.time()
    results = np.linalg.lstsq(X[:-1, :], X[:-1, -1])
    print time.time() - start

def test_cholesky(size, n_threads):
    X = np.random.rand(size + 1, size)
    x_t_x = np.cov(X.T)
    x_t_x_2 = np.copy(x_t_x)
    print "About to start cholesky"
    start = time.time()
    ch_x = np.asarray(cholesky.cholesky(x_t_x, n_threads)).T
    print "Cholesky time for size: ", size, time.time() - start
    real_ch_x = np.linalg.cholesky(x_t_x_2)
    assert(np.allclose(ch_x, real_ch_x))

test_cholesky(10000, 2)
