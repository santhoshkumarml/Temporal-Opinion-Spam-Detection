__author__ = 'santhosh'

import os
import sys
from datetime import datetime

import numpy

import AppUtil
import EvidenceUtil, RankHelper
from anomaly_detection import AnomalyDetector
from util import StatConstants


def checkAvgRatingValid(statistics_for_bnss):
    avg_rating = statistics_for_bnss[StatConstants.AVERAGE_RATING]
    if numpy.any(avg_rating > 5) or numpy.any(avg_rating < 0):
        print 'Rating invalid', statistics_for_bnss[StatConstants.BNSS_ID]
        # print avg_rating
        # sys.exit()
def doRanking(plotDir):
    bnss_to_reviews_dict = AppUtil.readReviewsForBnssOrUser(plotDir)
    ranked_bnss, bnss_first_time_dict, aux_info = RankHelper.rankAllAnomalies(plotDir)
    RankHelper.tryNewRanking(plotDir, ranked_bnss, aux_info)
    RankHelper.printRankedBnss(bnss_first_time_dict, ranked_bnss, aux_info,\
                               len(ranked_bnss), bnss_review_threshold=-1,\
                               bnss_to_reviews_dict=bnss_to_reviews_dict)

def doGatherEvidence(csvFolder, plotDir):
    evidencePlotDir = os.path.join(plotDir, 'Experiments')
    readReviewsText = False
    necessary_ds = EvidenceUtil.getNecessaryDs(csvFolder, readReviewsText=readReviewsText)
    ctg, superGraph, time_key_to_date_time,\
     suspicious_timestamps, suspicious_timestamp_ordered = necessary_ds
    bnss_key_time_wdw_list = [('284819997', (166, 171)),\
                              ('284819997', (173, 178)),\
                              ('319927587', (189, 194)),\
                              ('404593641', (158, 163)),\
                              ('412629178', (148, 153))]
    for bnss_key, time_key_wdw in bnss_key_time_wdw_list:
        EvidenceUtil.findStatsForEverything(evidencePlotDir,\
                                            bnss_key, time_key_wdw,\
                                            necessary_ds,\
                                            readReviewsText=readReviewsText,\
                                            doPlot=True)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: python -m \"tryout.testItunes\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]
    currentDateTime = datetime.now().strftime('%d-%b--%H:%M')
    plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), 'it')
#         AppUtil.extractAndSerializeBnssStatisticsForBnss(csvFolder, plotDir,\
#                                                      bnsses_list=['284235722'])
    AppUtil.detectAnomaliesForBnsses(csvFolder, plotDir, doPlot=True, logStats=False)
#     doRanking(plotDir)
    doGatherEvidence(csvFolder, plotDir)