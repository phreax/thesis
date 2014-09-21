import numpy as np
import math

def normalize_rows(matrix):
    maxvalues = np.max(matrix,axis=1).reshape(-1,1)
    maxvalues = np.maximum(maxvalues,np.ones(maxvalues.shape))
    return matrix / maxvalues

def pearson_corr(v1, v2):
    shared = []

    for i,r1 in enumerate(v1):
        r2 = v2[i]
        if r1 > 0.0 and r2 > 0.0:
            shared.append(i)

    n = len(shared)
    if n < 1:
        return 0.0

    # sum of all ratings
    sum1 = sum([v1[i] for i in shared])
    sum2 = sum([v2[i] for i in shared])

    r_avg1 = sum1/n
    r_avg2 = sum2/n

    sumCorr    = 0
    sumCorrSq1 = 0
    sumCorrSq2 = 0

    for i in shared:
        r1 = v1[i]
        r2 = v2[i]
        sumCorr   += (r1-r_avg1)*(r2-r_avg2)
        sumCorrSq1 += pow((r1-r_avg1),2)
        sumCorrSq2 += pow((r2-r_avg2),2)

    if sumCorr == 0.0:
        return 1.0

    return sumCorr/math.sqrt(sumCorrSq1*sumCorrSq2)

def cosine_sim(v1, v2):

    sum_ratings = np.sum(v1*v2)

    sq_ratings1 = np.sum(np.power(v1,2.0))
    sq_ratings2 = np.sum(np.power(v2,2.0))

    if sq_ratings1*sq_ratings2 > 0:
        return sum_ratings/(math.sqrt(sq_ratings1)*math.sqrt(sq_ratings2))
    return 0.0

def cosine_sim_ctx(v1, v2):

    sum_ratings = sum([sum(ru1) * sum(ru2) for ru1,ru2 in izip(v1,v2)])

    sq_ratings1 = sum([pow(r,2) for rc in v1 for r in rc])
    sq_ratings2 = sum([pow(r,2) for rc in v2 for r in rc])

    sim = sum_ratings/(sqrt(sq_ratings1)*sqrt(sq_ratings2))
    return sim

