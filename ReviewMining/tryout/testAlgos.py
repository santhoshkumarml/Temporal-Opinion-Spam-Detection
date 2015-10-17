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

CHPT_CONST_INCREASE = 'INCREASE_CONSTANT'
CHPT_CONST_DECREASE = 'DECREASE_CONSTANT'
CHPT_NORMAL_INCREASE = 'INCREASE_NORMAL'
CHPT_NORMAL_DECREASE = 'DECREASE_NORMAL'
OUTLIER_INCREASE = 'OUTLIER_INCREASE'
OUTLIER_DECREASE = 'OUTLIER_DECREASE'


AR = 'AR'
ARMA = 'ARMA'

def plotDataAndChanges(data, scores=[], changes=[]):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    # plt.yticks(numpy.arange(0, 3, 0.5))

    ax.plot(range(len(data)), data, 'b')

    if len(scores) > 0:
        ax2 = ax.twinx()
        # plt.yticks(numpy.arange(0, 3, 0.5))
        ax2.plot(range(len(scores)), scores,'g')

    for idx in changes:
        ax.axvline(x=idx, linewidth=2, color='r')
    plt.show()


def makeNormalData(mean=0.7, varaince =0.05, data_size=200, induced_outlier_or_chpts=[]):
    data = numpy.random.normal(mean, varaince, data_size)
    outlier_ch_idxs_visited = set()
    for idx in range(len(induced_outlier_or_chpts)):
        induced_outlier_ch_idx, induced_outlier_ch_magnitude, persistence_time, outlier_ch_type = induced_outlier_or_chpts[idx]

        assert induced_outlier_ch_idx not in outlier_ch_idxs_visited
        if outlier_ch_type == OUTLIER_INCREASE or outlier_ch_type == OUTLIER_DECREASE:
            assert persistence_time == 1
            if outlier_ch_type == OUTLIER_INCREASE:
                data[induced_outlier_ch_idx] = mean+induced_outlier_ch_magnitude
            else:
                data[induced_outlier_ch_idx] = mean-induced_outlier_ch_magnitude
            outlier_ch_idxs_visited.add(induced_outlier_ch_idx)
        elif outlier_ch_type == CHPT_CONST_INCREASE:
            start = induced_outlier_ch_idx
            end = start+persistence_time
            val = data[start-1] if start >=1 else mean
            data[start:end] = val+induced_outlier_ch_magnitude
            outlier_ch_idxs_visited |= set([indx for indx in range(start, end)])
        elif outlier_ch_type == CHPT_CONST_DECREASE:
            start = induced_outlier_ch_idx
            end = start+persistence_time
            val = data[start-1] if start >=1 else mean
            data[start:end] = val-induced_outlier_ch_magnitude
            outlier_ch_idxs_visited |= set([indx for indx in range(start, end)])
        elif outlier_ch_type == CHPT_NORMAL_INCREASE:
            start = induced_outlier_ch_idx
            end = start+persistence_time
            val = data[start-1] if start >=1 else mean
            data[start:end] = numpy.random.normal(val+induced_outlier_ch_magnitude, varaince, persistence_time)
            outlier_ch_idxs_visited |= set([indx for indx in range(start, end)])
        elif outlier_ch_type == CHPT_NORMAL_DECREASE:
            start = induced_outlier_ch_idx
            end = start+persistence_time
            val = data[start-1] if start >=1 else mean
            data[start:end] = numpy.random.normal(val-induced_outlier_ch_magnitude, varaince, persistence_time)
            outlier_ch_idxs_visited |= set([indx for indx in range(start, end)])
    return data


def runChangeFinder(data, algo):
    if algo == AR:
        r, order, smooth = 0.2, 1, 3
        cf = cfr.ChangeFinder(r, order, smooth)
    else:
        term, smooth, order = 4, 3, (2, 0)
        cf = cfr.ChangeFinderARIMA(term, smooth, order)

    change_scores = []
    for i in range(len(data)):
        score = cf.update(data[i])
        change_scores.append(score)
    chOutlierScores = change_scores
    return chOutlierScores


# change_scores = []

# data1 = makeNormalData(0.07, 0.05, 200,\
#                         induced_outlier_or_chpts=[(100,2,20,CHPT_NORMAL_INCREASE),\
#                                                 (140,3,20,CHPT_NORMAL_INCREASE)])



# data1 = makeNormalData(0.07, 0.05, 200,\
#                       induced_outlier_or_chpts=[(100,2,20,CHPT_NORMAL_INCREASE),\
#                                                 (140,3,20,CHPT_NORMAL_INCREASE)])
#
# data2 = makeNormalData(0.07, 0.05, 200,\
#                       induced_outlier_or_chpts=[(100,2,1,OUTLIER_INCREASE),\
#                                                 (140,3,1,OUTLIER_INCREASE),\
#                                                 (180,2,1,OUTLIER_INCREASE)])
#
#
# change_scores = runChangeFinder(data1, 'AR')
#
# alarms = [idx for idx in range(len(change_scores)) if change_scores[idx][1]]
# change_scores = [change_score for change_score, isAlarm in change_scores]
# plotDataAndChanges(data2, scores=change_scores, changes = alarms)
#
# change_scores = runChangeFinder(data2, 'AR')
# alarms = [idx for idx in range(len(change_scores)) if change_scores[idx][1]]
# change_scores = [change_score for change_score, isAlarm in change_scores]
# plotDataAndChanges(data2, scores=change_scores, changes = alarms)


#
# data2 = makeNormalData(0.07, 0.05, 200,\
#                       induced_outlier_or_chpts=[(100,2,20,CHPT_NORMAL_INCREASE),\
#                                                 (140,3,20,CHPT_NORMAL_INCREASE)])
# change_scores2 = runChangeFinder(data1, 'AR')
# plotDataAndChanges(data2, scores=change_scores2)
#
#
# data3 = makeNormalData(0.07, 0.05, 200,\
#                       induced_outlier_or_chpts=[(100,2,1,OUTLIER_INCREASE),\
#                                                 (140,3,1,OUTLIER_INCREASE),\
#                                                 (160,1,1,OUTLIER_INCREASE)])
# change_scores3 = runChangeFinder(data1, 'ARMA')
# plotDataAndChanges(data3, scores=change_scores3)
#
#
# data4 = makeNormalData(0.07, 0.05, 200,\
#                       induced_outlier_or_chpts=[(100,2,1,OUTLIER_DECREASE),\
#                                                 (160,3,1,OUTLIER_DECREASE)])
# change_scores4 = runChangeFinder(data1, 'ARMA')
# plotDataAndChanges(data4, scores=change_scores4)
#
#
# data5 = makeNormalData(0.07, 0.05, 200,\
#                       induced_outlier_or_chpts=[(20,2,1,OUTLIER_DECREASE),\
#                                                 (60,3,1,OUTLIER_INCREASE)])
# change_scores5 = runChangeFinder(data1, 'ARMA')
# plotDataAndChanges(data5, scores=change_scores5)

# change_scores = runChangeFinder(data1, 'AR')
#
# plotDataAndChanges(data, scores=change_scores)
#
# change_scores = runChangeFinder(data1, 'ARMA')
#
# plotDataAndChanges(data, scores=change_scores)





# def logloss(real_val, pred_val, v = 1):
#     import math
#     return -math.log(math.exp((-0.5*(real_val-pred_val)**2)/v)/math.sqrt(2*math.pi*v))
#
# from statsmodels.tsa.ar_model import AR
# from statsmodels.tsa.arima_model import ARMA
#
# data = [2.22974507,1.77638876,1.36251694,0.63430955,1.56276414,1.45049636
# ,1.49355146,1.33083748,1.45067782, 1.68305934,1.54421536,1.74168241
# ,1.37840367,1.40733197,1.50468499, 1.58443507,1.4767025, 1.66373543
# ,1.46783808,1.32792633,1.65257529, 1.68632441,1.9030402, 1.96999589
# ,1.84691613,2.07700135,2.23981053, 1.66073599,2.14179324,2.03673212
# ,2.14653166,2.14159997,2.13133767, 0.97888903,0.4334023, 0.65564258
# ,0.64874987,1.24975657,0.50703108, 0.77332397,1.10924767,0.81356824
# ,0.80387861,0.53311585,0.73540776, 0.79021073,1.23688976]
#
# data = [1.03328336,1.48207205,1.51375305,1.51579082,1.56124504,1.14842646,1.23729834,1.57941601,1.84673416,1.73875868,2.23399791,1.6364921, 1.15677965,1.52173791,1.51964453,0.89477794,1.21513233,1.2670422, 1.75034574,1.72928696,1.5224434,2.01607321,0.83662014,0.61629464,0.67232625,0.52825708,0.76687291,0.58897955,0.60068777,0.67027366]
#
# order = 3
# input_length = 20
# pred_length = 6
#
# ar_mod = AR(data[:input_length])
# ar_res = ar_mod.fit(ic='bic')
# print ar_res.fittedvalues()
# order = len(ar_res.params)
#
# print data
#
# # for idx in range(order, )
# # pred = []
#
#
# # arma_mod = ARMA(data[:20], order=(3, 2))
# # arma_res = arma_mod.fit()
# # pred = ar_mod_res.predict(order, len(data))
#
#
#
#
#
# params = ar_res.params
#
#
# def makeARPredictions(data, input_length, pred_length):
#     pred = list(data[:input_length])
#     pred = []
#     for i in range(0, input_length + pred_length - 1):
#         val = 0
#         for p in range(order):
#             val += data[i-(order - p - 1)] * params[p]
#         # val += numpy.random.normal(0, 1, 1)*math.exp(10**(-6))
#         pred.append(val)
#     return pred
#
#
# out = makeARPredictions(data, input_length, pred_length)
#
# scores = numpy.zeros(len(data))
# v = numpy.var(data[:input_length+pred_length])
#
# for i in range(order, input_length+pred_length-1):
#     score = logloss(data[i], out[i], v)
#     scores[i] = score
# # scores = out
#
# plotDataAndChanges(data, scores=scores)
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

def logStats(bnssKey, plotDir, chPtsOutliers):
    measure_log_file = open(os.path.join(plotDir, "measure_scores.log"), 'a')
    chPtsOutliers[StatConstants.BNSS_ID] = bnssKey
    measure_log_file.write(str(chPtsOutliers)+"\n")
    measure_log_file.close()
    del chPtsOutliers[StatConstants.BNSS_ID]

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
    # bnssKeys = ['386244833']
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

    bnssKeys = [file_name for file_name, size in file_list_size]

    bnssKeys = ['307906541']

    for bnss_key in bnssKeys:
        statistics_for_bnss = deserializeBnssStats(bnss_key, bnss_stats_dir)

        chPtsOutliers = detectAnomaliesForBnss(bnss_key, statistics_for_bnss, timeLength, find_outlier_idxs=True)

        # logStats(bnss_key, plotDir, chPtsOutliers)

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
    # doSerializeAllBnss(csvFolder, plotDir)
    tryBusinessMeasureExtractor(csvFolder, plotDir, doPlot=True)
    # print getThresholdForDifferentMeasures(plotDir, doHist=True)
    # RankHelper.rankAllAnomalies(plotDir)
    # bnss_stats_dir = os.path.join(plotDir, 'bnss_stats')
    # file_list_size = []
    # for root, dirs, files in os.walk(bnss_stats_dir):
    #     for name in files:
    #         file_list_size.append((name, os.path.getsize(os.path.join(bnss_stats_dir, name))))
    #     file_list_size = sorted(file_list_size, key= lambda x:x[1], reverse=True)
    #
    # bnssKeys = [file_name for file_name, size in file_list_size]
    # print bnssKeys[30:60]

    # bnssKeys = ['307906541']
