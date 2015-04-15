__author__ = 'santhosh'

from util import StatConstants
from datetime import datetime
import numpy


def extractMeasuresForBnss(usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict,\
                     superGraph, cross_time_graphs, plotDir, bnssKey, timeLength,\
                     measures_To_Be_Extracted = StatConstants.MEASURES):
    beforeStat = datetime.now()
    print 'Statistics for Bnss', bnssKey

