'''
Created on Feb 19, 2015

@author: santhosh
'''

from datetime import datetime
from util import StatConstants
import cusum

def detectChPtsAndOutliers(bnss_statistics):
    chPtsOutliers = dict()
    beforeDetection = datetime.now()
    for bnssKey in bnss_statistics:
        firstKey = bnss_statistics[bnssKey][StatConstants.FIRST_TIME_KEY]
        chPtsOutliers[bnssKey] = dict()
        for measure_key in StatConstants.MEASURES:
            if measure_key in bnss_statistics:
                ta, tai, taf, amp  = cusum.detect_cusum(bnss_statistics[bnssKey][measure_key][firstKey:],\
                                                                          threshold=1, drift=0, ending=True, show=False)
                print ta, tai, taf, amp
                chPtsOutliers[bnssKey][measure_key] = ([],[],[],[])
        
    afterDetection = datetime.now()
    print 'Time Taken For Anamoly Detection', afterDetection-beforeDetection
    return chPtsOutliers