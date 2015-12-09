from scipy.stats import linregress
import numpy as np
import time

import pyximport
pyximport.install()

from cholesky import cholesky 


def test_time():
    start = time.time()
    results = np.linalg.lstsq(X[:-1, :], X[:-1, -1])
    print time.time() - start

def test_cholesky():
    X = np.random.rand(100000000, 25)
    x_t_x = np.cov(X)
    x_t_x_2 = np.copy(x_t_x)
    ch_x = cholesky(x_t_x, 1)
    real_ch_x = np.linalg.cholesky(x_t_x_2)
    assert(np.array_equal(ch_x, real_ch_x))

test_cholesky()
