import cython
from cython.parallel import prange, parallel
from libc.math cimport sqrt

import numpy as np
cimport numpy as np

@cython.wraparound(False)
@cython.boundscheck(False)
cpdef f_cholesky(np.float64_t[:, :] mat, int num_threads):
    cholesky(mat, num_threads)

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef cholesky2(np.float64_t[:, :] in_mat, np.float64_t[:, :] out_mat, int num_threads):
    cdef:
        int i, k, j, l
        int ix, jx
        int rows, cols 
        float s1, s2
    rows = in_mat.shape[0]
    cols = in_mat.shape[1]
    with nogil:
        for i in xrange(rows):
            s1 = 0.0
            for j in xrange(i):
                s1 += out_mat[i, j] * out_mat[i, j]
            out_mat[i, i] = sqrt(in_mat[i, i] - s1)

            for k in prange(i+1, rows, num_threads=num_threads, schedule='static'):
                s2 = 0.0
                for l in prange(i):
                    s2 += out_mat[k, l] * out_mat[i, l]
                out_mat[k, i] = (1.0/out_mat[i, i] * (in_mat[k, i] - s2))

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
