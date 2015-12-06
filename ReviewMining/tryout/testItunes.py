__author__ = 'santhosh'

import os
import sys
from datetime import datetime

import AppUtil, RankHelper
from anomaly_detection import AnomalyDetector
from util import StatConstants

def tryBusinessMeasureExtractor(csvFolder, plotDir, doPlot, timeLength = '1-W'):
    measuresToBeExtracted = [measure for measure in StatConstants.MEASURES \
                             if measure != StatConstants.MAX_TEXT_SIMILARITY and measure != StatConstants.TF_IDF]
    lead_signals = [measure for measure in measuresToBeExtracted if measure in StatConstants.MEASURE_LEAD_SIGNALS]
    measuresToBeExtracted = [measure for measure in set(lead_signals).union(set(measuresToBeExtracted))]

    bnss_stats_dir = os.path.join(plotDir, AppUtil.ITUNES_BNSS_STATS_FOLDER)
    file_list_size = []
    for root, dirs, files in os.walk(bnss_stats_dir):
        for name in files:
            file_list_size.append((name, os.path.getsize(os.path.join(bnss_stats_dir, name))))
        file_list_size = sorted(file_list_size, key=lambda x: x[1], reverse=True)

    bnssKeys = [file_name for file_name,
                              size in file_list_size]
    bnssKeys = ['379459295']
    for bnss_key in bnssKeys:
        print '--------------------------------------------------------------------------------------------------------'
        statistics_for_bnss = AppUtil.deserializeBnssStats(bnss_key,
                                                           os.path.join(plotDir, AppUtil.ITUNES_BNSS_STATS_FOLDER))
        chPtsOutliers = AnomalyDetector.detectChPtsAndOutliers(statistics_for_bnss, timeLength,
                                                               find_outlier_idxs=True)
        # AppUtil.logStats(bnss_key, plotDir, chPtsOutliers, statistics_for_bnss[StatConstants.FIRST_TIME_KEY])
        if doPlot:
            AppUtil.plotBnssStats(bnss_key, statistics_for_bnss, chPtsOutliers, plotDir,
                                  measuresToBeExtracted, timeLength)
        print '--------------------------------------------------------------------------------------------------------'

def tryNewRanking(ranked_bnss, aux_info):
    scores = dict()
    import pickle, math
    for bnss_key, timeWindow in ranked_bnss:
        f = open(os.path.join( os.path.join(plotDir, 'bnss_stats'),
                               bnss_key))
        statistics_for_bnss = pickle.load(f)
        firstTimeKey = statistics_for_bnss[StatConstants.FIRST_TIME_KEY]
        score = aux_info[(bnss_key, timeWindow)]

        idx1, idx2 = timeWindow
        idx1 = idx1 + firstTimeKey
        idx2 = idx2 + firstTimeKey
        timeWindow = (idx1, idx2)
        top_number_of_reviews = max([statistics_for_bnss[StatConstants.NON_CUM_NO_OF_REVIEWS][idx]
                                     for idx in range(idx1, idx2)
                                     if idx < len(statistics_for_bnss[StatConstants.NON_CUM_NO_OF_REVIEWS])])
        score = score[0] * top_number_of_reviews

        scores[(bnss_key, timeWindow)] = score
        f.close()

    sorted_scores = sorted(scores.keys(), key=lambda key:scores[key], reverse=True)
    for bnss_key, timeWindow in sorted_scores:
        print bnss_key, timeWindow, scores[(bnss_key, timeWindow)]


def doLogUsrAndBnssReview(csvFolder, plotDir):
    from util import SIAUtil
    bnssReviewLogDir = os.path.join(plotDir, 'bnss_review_logs')
    usrReviewLogDir = os.path.join(plotDir, 'usr_review_logs')
    if not os.path.exists(bnssReviewLogDir):
        os.mkdir(bnssReviewLogDir)
    AppUtil.logAllUsrOrBnssStats(csvFolder, bnssReviewLogDir, node_type=SIAUtil.PRODUCT)
    if not os.path.exists(usrReviewLogDir):
        os.mkdir(usrReviewLogDir)
    AppUtil.logAllUsrOrBnssStats(csvFolder, usrReviewLogDir, node_type=SIAUtil.USER)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: python -m \"tryout.testItunes\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]
    currentDateTime = datetime.now().strftime('%d-%b--%H:%M')
    plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), 'it')

    # tryBusinessMeasureExtractor(csvFolder, plotDir, doPlot=True)

    doLogUsrAndBnssReview(csvFolder, plotDir)
    # AppUtil.readData(csvFolder, readReviewsText=True)
    # bnss_to_reviews_dict = AppUtil.readReviewsForBnssOrUser(plotDir)
    # ranked_bnss, bnss_first_time_dict, aux_info = RankHelper.rankAllAnomalies(plotDir)
    # tryNewRanking(ranked_bnss, aux_info)

    # RankHelper.printRankedBnss(bnss_first_time_dict, ranked_bnss, aux_info, len(ranked_bnss),
    #                             bnss_review_threshold=-1, bnss_to_reviews_dict=bnss_to_reviews_dict)