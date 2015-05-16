__author__ = 'santhosh'

import numpy
import random

def getSyntheticData(no_of_series, series_length, insert_random_anom = True):
    means = [3 for i in range(no_of_series)]
    covariance = numpy.diag([0.05 for i in range(no_of_series)])
    data = numpy.random.multivariate_normal(means, covariance, size=series_length).T
    print data
    anom_idx = random.randrange(series_length/2+2, series_length/2+7, 1)
    data[:,[anom_idx]] = 7
    return data




