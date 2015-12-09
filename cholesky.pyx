from cython.parallel import prange
from libc.math cimport sqrt

import numpy as np
cimport numpy as np

cpdef np.float64_t[:, :] cholesky(np.float64_t[:, :] mat, int num_threads):
    cdef: 
        # put definitions in here 
        int i, j, k
        int rows, cols
    rows = mat.shape[0]
    cols = mat.shape[1]
    with nogil:
        for i in range(rows):
            mat[i,i] = sqrt(mat[i, i])
            # each iteration updates/writes to same part of matrix 
            for j in prange(i+1, rows, num_threads=num_threads):
                mat[i, j] = mat[i, j] / mat[i, i]
            # will never update before reading 
            for k in prange(i+1, rows, num_threads=num_threads):
                for j in prange(k, rows, num_threads=num_threads):
                    mat[k, j] = mat[k, j] - (mat[i, k] * mat[i, j])
        # zero out lower part of matrix  
        for i in prange(rows, num_threads=num_threads):
            for j in prange(i, num_threads=num_threads):
                mat[i, j] = 0.0
    return mat 
