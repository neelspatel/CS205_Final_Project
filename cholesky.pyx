import cython
from cython.parallel import prange, parallel
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
        int i, j, k, l
        int ix, jx
        int rows, cols
    rows = mat.shape[0]
    cols = mat.shape[1]
    with nogil:
        # can't parallelize outer loop
        for i in xrange(rows):
            mat[i,i] = sqrt(mat[i, i])
            # each iteration updates/writes to same part of matrix 
            for j in xrange(i+1, rows):
                mat[i, j] = mat[i, j] / mat[i, i]

            # will never update before reading 
            for k in prange(i+1, rows, num_threads=num_threads, schedule='static'):
                for l in xrange(k, rows):
                    mat[k, l] = mat[k, l] - (mat[i, k] * mat[i, l])

        # zero out lower part of matrix  
        for ix in prange(rows, num_threads=num_threads, schedule='static'):
            for jx in xrange(ix):
                mat[ix, jx] = 0.0
