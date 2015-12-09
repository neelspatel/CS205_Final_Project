import cython
from cython.parallel import prange
from libc.math cimport sqrt

import numpy as np
cimport numpy as np

@cython.boundscheck(False)
cpdef f_cholesky(np.float64_t[:, :] mat, int num_threads):
    cholesky(mat, num_threads)

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef cholesky(np.float64_t[:, :] mat, int num_threads):
    cdef: 
        int i, j, k
        int rows, cols
    rows = mat.shape[0]
    cols = mat.shape[1]
    with nogil:
        for i in xrange(rows):
            mat[i,i] = sqrt(mat[i, i])
            # each iteration updates/writes to same part of matrix 
            for j in xrange(i+1, rows):
                mat[i, j] = mat[i, j] / mat[i, i]

            # will never update before reading 
            for k in prange(i+1, rows, num_threads=num_threads):
                for j in xrange(k, rows):
                    mat[k, j] = mat[k, j] - (mat[i, k] * mat[i, j])
        # zero out lower part of matrix  
        #for i in prange(rows, num_threads=num_threads):
        for i in prange(rows, num_threads=num_threads):
            for j in xrange(i):
                mat[i, j] = 0.0
