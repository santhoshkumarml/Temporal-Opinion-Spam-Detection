'''
Created on Feb 19, 2015

@author: santhosh
'''

from datetime import datetime
from util import StatConstants
import cusum
import changefinder



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
                cf = changefinder.ChangeFinder(r = 0.5, order = 1, smooth = 5)
                change_idxs = []
                for i in range(len(data)):
                    score = cf.update(data[i])
                    if score > 0:
                        change_idxs.append(i)
                chPtsOutliers[bnssKey][measure_key] = change_idxs 
        
    afterDetection = datetime.now()
    print 'Time Taken For Anamoly Detection', afterDetection-beforeDetection
    return chPtsOutliers
