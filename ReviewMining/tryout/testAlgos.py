__author__ = 'santhosh'

import numpy
import matplotlib.pyplot as plt

from anomaly_detection import AnomalyDetector
from util import StatConstants
from anomaly_detection import ChangeFinder as cfr


# import changefinder
import RankHelper
import math
from statistics import business_statistics_generator
from util import GraphUtil
from itunes_utils.ItunesDataReader import ItunesDataReader
import os
from util import SIAUtil
from util import PlotUtil
from datetime import datetime
import sys
import pickle


def doHistogramForMeasure(bins, algo, measure_key, scores):
    fig = plt.figure()
    plt.title('Score histogram')
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlabel(measure_key)
    # ax.set_xticks(bins)
    # if key == StatConstants.NO_OF_NEGATIVE_REVIEWS or key == StatConstants.NO_OF_POSITIVE_REVIEWS\
    #     or key == StatConstants.NON_CUM_NO_OF_REVIEWS:
    #     ax.hist(scores, bins, alpha=1.00, label=key, log=True)
    # else:
    print algo, measure_key
    thr1 = getThreshold(scores, 0.20)
    thr2 = getThreshold(scores, 0.15)
    thr3 = getThreshold(scores, 0.10)
    thr4 = getThreshold(scores, 0.05)
    if measure_key in [StatConstants.NO_OF_POSITIVE_REVIEWS, StatConstants.NO_OF_NEGATIVE_REVIEWS,
                       StatConstants.NON_CUM_NO_OF_REVIEWS]:
        # scores = [math.log(sc+1) for sc in scores]
        min_score = min(scores)
        max_score = max(scores)
        # thr1 = math.log(thr1+1)
        # thr2 = math.log(thr2+1)
        # thr3 = math.log(thr3+1)
        # bins = numpy.arange(min_score, max_score, bins)
        # bins = bins[:11]
        ax.hist(scores, bins, alpha=1.00, label=algo+' '+measure_key)
    else:
        ax.hist(scores, bins, alpha=1.00, label=algo+' '+measure_key)

    ax.axvline(x=thr1, linewidth=2, color='r')
    ax.axvline(x=thr2, linewidth=2, color='g')
    ax.axvline(x=thr3, linewidth=2, color='c')
    plt.show()

def getThreshold(stats_for_dimension, k):
    m = numpy.mean(stats_for_dimension)
    std = numpy.std(stats_for_dimension)
    vals = {0.05:math.sqrt(19),0.10:3, 0.20:2, 0.15:2.38}
    return (m + (vals[k]*std))


def readScoresFromMeasureLog(plotDir, file_name):
    chPtsOutliers = dict()
    measure_scores = dict()
    measure_log = os.path.join(plotDir, file_name)
    with open(measure_log) as f:
        strings = f.readlines()
        # strings = f.read()
        # p = re.compile('[{][^{]+([{][^{]+[}])+[^}]+BNSS_ID[^}]+[}]')
        # p = re.compile('[{].*BNSS_ID[^}]+[}]')
        # strings = p.findall(a)
        for string in strings:
            string.strip('\r')
            string.strip('\n')
            string = "chPtsOutliers="+string
            try:
                exec(string)
            except:
                continue
            avg_idxs, chOutlierScores = chPtsOutliers[StatConstants.AVERAGE_RATING][StatConstants.CUSUM]
            diff_test_idxs = set()
            for idx in sorted(avg_idxs):
                idx1, idx2 = AnomalyDetector.getRangeIdxs(idx)
                for indx in range(idx1, idx2+1):
                    diff_test_idxs.add(indx)

            for measure_key in chPtsOutliers.keys():
                if measure_key == StatConstants.AVERAGE_RATING \
                        or measure_key == StatConstants.NO_OF_REVIEWS or \
                                measure_key == 'BNSS_ID':
                    continue

                chPtsOutliersEntry = chPtsOutliers[measure_key]
                for algo in chPtsOutliersEntry.keys():
                    chOutlierIdxs, chOutlierScores = chPtsOutliersEntry[algo]

                    if measure_key not in measure_scores:
                        measure_scores[measure_key] = dict()

                    if algo not in measure_scores[measure_key]:
                        measure_scores[measure_key][algo] = []

                    test_measure_scores = []


                    if algo == StatConstants.LOCAL_AR:
                        test_measure_scores = [chOutlierScores[idx] for idx in range(len(chOutlierScores)) \
                                               if idx in diff_test_idxs]
                    else:
                        test_measure_scores = chOutlierScores

                    test_measure_scores = [score for score in test_measure_scores]

                    measure_scores[measure_key][algo].extend(test_measure_scores)

    # for measure_key in measure_scores.keys():
    #     print measure_key, max(measure_scores[measure_key]), min(measure_scores[measure_key])

    return measure_scores

def readData(csvFolder):
    rdr = ItunesDataReader()
    (usrIdToUserDict, bnssIdToBusinessDict, reviewIdToReviewsDict) = rdr.readData(csvFolder, readReviewsText=False)
    return bnssIdToBusinessDict, reviewIdToReviewsDict, usrIdToUserDict

def logStats(bnssKey, plotDir, chPtsOutliers, firstTimeKey):
    measure_log_file = open(os.path.join(plotDir, "scores_with_outliers.log"), 'a')
    chPtsOutliers[StatConstants.BNSS_ID] = bnssKey
    chPtsOutliers[StatConstants.FIRST_TIME_KEY] = firstTimeKey
    measure_log_file.write(str(chPtsOutliers)+"\n")
    measure_log_file.close()
    del chPtsOutliers[StatConstants.BNSS_ID]
    del chPtsOutliers[StatConstants.FIRST_TIME_KEY]

def detectAnomaliesForBnss(bnssKey, statistics_for_current_bnss, timeLength, find_outlier_idxs=True):
    beforeAnomalyDetection = datetime.now()

    chPtsOutliers = AnomalyDetector.detectChPtsAndOutliers(statistics_for_current_bnss, timeLength,
                                                           find_outlier_idxs)
    afterAnomalyDetection = datetime.now()

    print 'Anomaly Detection Time for bnss:', bnssKey, 'in', afterAnomalyDetection-beforeAnomalyDetection

    return chPtsOutliers


def plotBnssStats(bnss_key, statistics_for_bnss, chPtsOutliers, plotDir, measuresToBeExtracted, timeLength):
    beforePlotTime = datetime.now()
    avg_idxs, chOutlierScores = chPtsOutliers[StatConstants.AVERAGE_RATING][StatConstants.CUSUM]

    PlotUtil.plotMeasuresForBnss(statistics_for_bnss, chPtsOutliers, plotDir, \
                                 measuresToBeExtracted, avg_idxs, timeLength)
    afterPlotTime = datetime.now()
    print 'Plot Generation Time for bnss:', bnss_key, 'in', afterPlotTime-beforePlotTime


def serializeBnssStats(bnss_key, plotDir, statistics_for_bnss):
    bnss_file_name = os.path.join(plotDir, bnss_key)
    print 'Serializing to file', bnss_file_name
    if not os.path.exists(bnss_file_name):
        with open(bnss_file_name, 'w') as f:
            pickle.dump(statistics_for_bnss, f)

def deserializeBnssStats(bnss_key, statsDir):
    return pickle.load(open(os.path.join(statsDir, bnss_key)))

def readAndGenerateStatistics(csvFolder, plotDir, timeLength = '1-W'):
    # Read data
    bnssIdToBusinessDict, reviewIdToReviewsDict, usrIdToUserDict = readData(csvFolder)
    # Construct Graphs
    superGraph, cross_time_graphs = GraphUtil.createGraphs(usrIdToUserDict, \
                                                           bnssIdToBusinessDict, \
                                                           reviewIdToReviewsDict, timeLength)
    if not os.path.exists(plotDir):
        os.makedirs(plotDir)
    bnssKeys = [bnss_key for bnss_key, bnss_type in superGraph.nodes() \
                if bnss_type == SIAUtil.PRODUCT]
    bnssKeys = sorted(bnssKeys, reverse=True, key=lambda x: len(superGraph.neighbors((x, SIAUtil.PRODUCT))))
    # bnssKeys = ['363590051']
    # bnssKeys = bnssKeys[:2]
    measuresToBeExtracted = [measure for measure in StatConstants.MEASURES \
                             if measure != StatConstants.MAX_TEXT_SIMILARITY and measure != StatConstants.TF_IDF]
    lead_signals = [measure for measure in measuresToBeExtracted if measure in StatConstants.MEASURE_LEAD_SIGNALS]
    measuresToBeExtracted = [measure for measure in set(lead_signals).union(set(measuresToBeExtracted))]
    return bnssKeys, cross_time_graphs, measuresToBeExtracted, superGraph

def doSerializeAllBnss(csvFolder, plotDir, timeLength = '1-W'):
    bnssKeys, cross_time_graphs, measuresToBeExtracted, superGraph = readAndGenerateStatistics(csvFolder, plotDir)
    for bnssKey in bnssKeys:
        statistics_for_bnss = business_statistics_generator.extractBnssStatistics(
            superGraph, \
            cross_time_graphs, \
            plotDir, bnssKey, \
            timeLength, \
            measuresToBeExtracted, logStats=False)
        serializeBnssStats(bnssKey, plotDir, statistics_for_bnss)


def intersection_between_users(usr_ids_for_bnss_in_time_window, bnssKey, superGraph):
    usrs_for_this_bnss = set([usrId for usrId, usr_type in superGraph.neighbors((bnssKey, SIAUtil.PRODUCT))])
    ins = usr_ids_for_bnss_in_time_window.intersection(usrs_for_this_bnss)
    if len(ins) > 10:
        print bnssKey, ins
    return len(ins)

def findUsersInThisTimeWindow(bnssKey, time_window, csvFolder, plotDir, timeLength = '1-W'):
     # Read data
    bnssIdToBusinessDict, reviewIdToReviewsDict, usrIdToUserDict = readData(csvFolder)

    # Construct Graphs
    superGraph, cross_time_graphs = GraphUtil.createGraphs(usrIdToUserDict, \
                                                           bnssIdToBusinessDict, \
                                                           reviewIdToReviewsDict, timeLength)

    usr_ids_for_bnss_in_time_window = []

    lb, ub = time_window
    time_window = [idx for idx in range(lb, ub+1)]
    for time_key in time_window:
         time_g = cross_time_graphs[time_key]
         usr_ids_for_bnss_in_time_window = usr_ids_for_bnss_in_time_window \
                                           + [usrId for (usrId, usr_type)
                                              in time_g.neighbors((bnssKey, SIAUtil.PRODUCT))]
    usr_ids_for_bnss_in_time_window = set(usr_ids_for_bnss_in_time_window)
    bnssKeys = set([bnssId for usrId in usr_ids_for_bnss_in_time_window for bnssId, bnssType in superGraph.neighbors((usrId, SIAUtil.USER))])
    bnssKeys = [(bnssId, intersection_between_users(usr_ids_for_bnss_in_time_window, bnssId, superGraph)) for bnssId in bnssKeys]
    bnssKeys = sorted(bnssKeys, reverse=True,
                      key= lambda x: x[1])
    print bnssKeys



def getThresholdForDifferentMeasures(plotDir, doHist=False):
    measure_scores = readScoresFromMeasureLog(plotDir, "measure_scores.log")
    result = dict()
    measure_noise_threshold = {StatConstants.NO_OF_NEGATIVE_REVIEWS:10000 ,
                               StatConstants.NON_CUM_NO_OF_REVIEWS:2652956,
                               StatConstants.NO_OF_POSITIVE_REVIEWS:2652956}
    for measure_key in measure_scores.keys():
        for algo in measure_scores[measure_key].keys():
            if(algo  == StatConstants.LOCAL_AR):
                continue
            scores = measure_scores[measure_key][algo]
            #StatConstants.NO_OF_NEGATIVE_REVIEWS ,StatConstants.NON_CUM_NO_OF_REVIEWS, StatConstants.NO_OF_POSITIVE_REVIEWS
            #[-ve -> 10000, +ve-> 2652956,,all->265296]
            #
            # if not measure_key in [StatConstants.NO_OF_NEGATIVE_REVIEWS ,StatConstants.NON_CUM_NO_OF_REVIEWS, StatConstants.NO_OF_POSITIVE_REVIEWS]:
            #     continue
            # else:
                # print numpy.histogram(scores, 500)
                # sys.exit()
            if measure_key in measure_noise_threshold:
                scores = [sc for sc in scores if sc < measure_noise_threshold[measure_key]]
            thr = getThreshold(scores, 0.15)
            if doHist:
                doHistogramForMeasure(20, algo, measure_key, scores)
            result[measure_key] = thr
    return result

def tryBusinessMeasureExtractor(csvFolder, plotDir, doPlot, timeLength = '1-W'):
    measuresToBeExtracted = [measure for measure in StatConstants.MEASURES \
                             if measure != StatConstants.MAX_TEXT_SIMILARITY and measure != StatConstants.TF_IDF]
    lead_signals = [measure for measure in measuresToBeExtracted if measure in StatConstants.MEASURE_LEAD_SIGNALS]
    measuresToBeExtracted = [measure for measure in set(lead_signals).union(set(measuresToBeExtracted))]

    bnss_stats_dir = os.path.join(plotDir, 'bnss_stats')
    file_list_size = []
    for root, dirs, files in os.walk(bnss_stats_dir):
        for name in files:
            file_list_size.append((name, os.path.getsize(os.path.join(bnss_stats_dir, name))))
        file_list_size = sorted(file_list_size, key= lambda x:x[1], reverse=True)

    bnssKeys = [file_name for file_name,
                              size in file_list_size]

    # bnssKeys = ['481012158']
    # bnssKeys = ['316239742', '351598228', '391704995', '399734002', '481096722',
    #             '326477287', '385786751', '477148788', '481589275', '448679509']
    bnssKeys = ['363590051', '351598228', '337950299', '374091507',
                '481012158', '320578069', '449453028', '316937016',
                '481012158', '433701402', '334982585', '494481220',
                '394900607', '403654673', '481012158', '481185291',
                '329643619', '494481220', '481185291']
    bnssKeys = ['481012158']

    print '---------------------------------------------------------------------------------------------------------------'
    for bnss_key in bnssKeys:
        statistics_for_bnss = deserializeBnssStats(bnss_key, bnss_stats_dir)

        chPtsOutliers = detectAnomaliesForBnss(bnss_key, statistics_for_bnss, timeLength, find_outlier_idxs=True)

        # logStats(bnss_key, plotDir, chPtsOutliers, statistics_for_bnss[StatConstants.FIRST_TIME_KEY])

        if doPlot:
            plotBnssStats(bnss_key, statistics_for_bnss, chPtsOutliers, plotDir, measuresToBeExtracted, timeLength)

    print '---------------------------------------------------------------------------------------------------------------'


if __name__ == "__main__":
    if(len(sys.argv)!=2):
        print 'Usage: python -m \"tryout.testAlgos\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]
    currentDateTime = datetime.now().strftime('%d-%b--%H:%M')
    plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), '1')
    tryBusinessMeasureExtractor(csvFolder, plotDir, doPlot=False)
    # findUsersInThisTimeWindow('363590051',(107, 112),csvFolder, plotDir)
    # RankHelper.rankAllAnomalies(plotDir)
    # doSerializeAllBnss(csvFolder, plotDir)
    # print getThresholdForDifferentMeasures(plotDir, doHist=True)