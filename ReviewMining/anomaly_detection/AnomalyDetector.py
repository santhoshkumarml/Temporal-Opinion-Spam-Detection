'''
Created on Feb 19, 2015

@author: santhosh
'''

from datetime import datetime
from util import StatConstants
import anomaly_detection
import changefinder
import cusum
import numpy

def detect_outliers_using_cusum(x, threshold=1):
    x = numpy.atleast_1d(x).astype('float64')
    gp, gn = numpy.zeros(x.size), numpy.zeros(x.size)
    ta, tai, tapi, tani = numpy.array([[], [], [], []], dtype=int)
    tap, tan = 0, 0
    # Find changes (online form)
    for i in range(1, x.size):
        s = x[i] - x[i-1]
        gp[i] = gp[i-1] + s  # cumulative sum for + change
        gn[i] = gn[i-1] - s  # cumulative sum for - change
        if gp[i] < 0:
            gp[i], tap = 0, i
        if gn[i] < 0:
            gn[i], tan = 0, i
        if gp[i] > threshold or gn[i] > threshold:  # change detected!
            ta = numpy.append(ta, i)    # alarm index
            if gp[i] > threshold:
                tai = numpy.append(tai, tap)
                tapi = numpy.append(tapi,i)
            else:
                tai = numpy.append(tai, tan)
                tani = numpy.append(tani,i)
            gp[i], gn[i] = 0, 0      # reset alarm
    return ta, tai, tapi, tani
            
# r - Coefficient of forgetting type AR model. 0 <r <1
# order - Degree of forgetting type AR model
# smooth - section length of time to be moving average smoothing the calculated outliers score

def detectChPtsAndOutliers(bnss_statistics):
    chPtsOutliers = dict()
    beforeDetection = datetime.now()
    for bnssKey in bnss_statistics:
        firstKey = bnss_statistics[bnssKey][StatConstants.FIRST_TIME_KEY]
        chPtsOutliers[bnssKey] = dict()
        for measure_key in StatConstants.MEASURES:
            if measure_key in bnss_statistics[bnssKey]:
                data = bnss_statistics[bnssKey][measure_key][firstKey:]
                algo, params = StatConstants.MEASURES_CHANGE_FINDERS[measure_key]
                if algo == StatConstants.AR_UNIFYING:
                    r,order,smooth = params
                    cf = changefinder.ChangeFinder(r,order,smooth)
                    change_scores = []
                    for i in range(len(data)):
                        score = cf.update(data[i])
                        change_scores.append(score)
                    chPtsOutliers[bnssKey][measure_key] = change_scores
                elif algo == StatConstants.CUSUM:
                    chPtsOutliers[bnssKey][measure_key] = cusum.detect_cusum(data, threshold=params, show=False)

    
    afterDetection = datetime.now()
    print 'Time Taken For Anamoly Detection', afterDetection-beforeDetection
    return chPtsOutliers
