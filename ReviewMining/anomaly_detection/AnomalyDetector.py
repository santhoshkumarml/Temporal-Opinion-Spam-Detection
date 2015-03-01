'''
Created on Feb 19, 2015

@author: santhosh
'''

from datetime import datetime
from util import StatConstants
import anomaly_detection
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
                r,order,smooth = StatConstants.MEASURES_CHANGE_FINDERS[measure_key]
                cf = changefinder.ChangeFinder(r,order,smooth)
                change_scores = []
                for i in range(len(data)):
                    score = cf.update(data[i])
                    change_scores.append(score)
                chPtsOutliers[bnssKey][measure_key] = change_scores 
    
    afterDetection = datetime.now()
    print 'Time Taken For Anamoly Detection', afterDetection-beforeDetection
    return chPtsOutliers
