import numpy as np

def normalize_col_stochastic(matrix):
    n,m = matrix.shape

    matrix = matrix.copy()

    # add uniform distribution to avoid zero rows
    matrix[:] += 1.0/n

    for i in xrange(m):
        colsum = np.sum(matrix[:,i])
        matrix[:,i] *= 1./colsum

    return matrix

def add_damping_factor(matrix, d=0.85):
    n = matrix.shape[0]
    return matrix*d + (((1.0-d)/n)*np.ones((n,n)))

def pagerank_power(matrix, p, max_iter=10):

    eps = 0.0001
    n = matrix.shape[0]
    v = np.ones((n,1)) * 1.0/n
    d = 0.85

    v_new = matrix * v

    i = 0
    while(np.linalg.norm(v-v_new) > eps and i < max_iter):
        v = v_new
        v_new = d*matrix * v + (1.0-d)*p
        i += 1


    return v_new
