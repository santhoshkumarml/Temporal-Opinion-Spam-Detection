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


def tryBusinessMeasureExtractor(csvFolder, plotDir, logStats=False, doPlot=False, timeLength = '1-W', bnss_list = list()):
    measuresToBeExtracted = [measure for measure in StatConstants.MEASURES \
                             if measure != StatConstants.MAX_TEXT_SIMILARITY and measure != StatConstants.TF_IDF]
    lead_signals = [measure for measure in measuresToBeExtracted if measure in StatConstants.MEASURE_LEAD_SIGNALS]
    measuresToBeExtracted = [measure for measure in set(lead_signals).union(set(measuresToBeExtracted))]

    bnss_stats_dir = os.path.join(plotDir, AppUtil.ITUNES_BNSS_STATS_FOLDER)
    if len(bnss_list) == 0:
        file_list_size = []
        for root, dirs, files in os.walk(bnss_stats_dir):
            for name in files:
                file_list_size.append((name, os.path.getsize(os.path.join(bnss_stats_dir, name))))
            file_list_size = sorted(file_list_size, key=lambda x: x[1], reverse=True)

        bnssKeys = [file_name for file_name,
                                  size in file_list_size]
        bnssKeys = ['284235722']
    else:
        bnssKeys = bnss_list

    for bnss_key in bnssKeys:
        print '--------------------------------------------------------------------------------------------------------'
        statistics_for_bnss = AppUtil.deserializeBnssStats(bnss_key,
                                                           os.path.join(plotDir, AppUtil.ITUNES_BNSS_STATS_FOLDER))

        chPtsOutliers = AnomalyDetector.detectChPtsAndOutliers(statistics_for_bnss, timeLength,
                                                               find_outlier_idxs=True)
        if doPlot:
            AppUtil.plotBnssStats(bnss_key, statistics_for_bnss, chPtsOutliers, plotDir,
                                  measuresToBeExtracted, timeLength)
        if logStats:
            AppUtil.logStats(bnss_key, plotDir, chPtsOutliers, statistics_for_bnss[StatConstants.FIRST_TIME_KEY])
        print '--------------------------------------------------------------------------------------------------------'


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: python -m \"tryout.testItunes\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]
    currentDateTime = datetime.now().strftime('%d-%b--%H:%M')
    plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), 'it')

#     tryBusinessMeasureExtractor(csvFolder, plotDir, doPlot=True, logStats=False)
#     AppUtil.extractAndSerializeBnssStatisticsForBnss(csvFolder, plotDir, bnsses_list=['284235722'])

#     bnss_to_reviews_dict = AppUtil.readReviewsForBnssOrUser(plotDir)
#     ranked_bnss, bnss_first_time_dict, aux_info = RankHelper.rankAllAnomalies(plotDir)
#     RankHelper.tryNewRanking(plotDir, ranked_bnss, aux_info)

#     RankHelper.printRankedBnss(bnss_first_time_dict, ranked_bnss, aux_info, len(ranked_bnss),
#                                 bnss_review_threshold=-1, bnss_to_reviews_dict=bnss_to_reviews_dict)
    doGatherEvidence(csvFolder, plotDir)