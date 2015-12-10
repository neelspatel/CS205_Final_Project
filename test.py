from scipy.stats import linregress
import numpy as np
import time
import cython
import sys

import set_compiler
set_compiler.install()

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
    cholesky.cholesky(x_t_x, n_threads)
    #ch_x = np.asarray(cholesky.cholesky(x_t_x, n_threads)).T
    print "Cholesky time for size: ", size, time.time() - start
    start = time.time()
    real_ch_x = np.linalg.cholesky(x_t_x_2)
    print "Theirs took: ", time.time() - start
    assert(np.allclose(x_t_x.T, real_ch_x))

def test_cholesky2(size, n_threads):
    X = np.random.rand(size + 1, size)
    x_t_x = np.cov(X.T)
    out_mat = np.zeros(x_t_x.shape)
    print "Cholesky"
    start = time.time()
    cholesky.cholesky2(x_t_x, out_mat, n_threads)
    print time.time() - start 
    real_ch_x = np.linalg.cholesky(x_t_x_2)
    assert(np.allclose(out_mat.T, real_ch_x))

size = 1000
num_threads = 2
print "1 thread"
test_cholesky(size, 1) 
print num_threads, " threads"
test_cholesky(size, num_threads) 
