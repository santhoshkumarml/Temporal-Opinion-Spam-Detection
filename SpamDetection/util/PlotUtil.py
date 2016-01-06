'''
Created on Jan 10, 2015

@author: Santhosh
'''

import matplotlib.pyplot as plt
from os.path import join
from util import StatConstants
import numpy
from datetime import datetime, timedelta
import random
from anomaly_detection import AnomalyDetector

import GraphUtil
import matplotlib.dates as mdates


# def plotReviewTimeVelocity(bnss_statistics, bnssIdToBusinessDict,\
#                         bnss_key, total_time_slots, inputDir, clr):
#
#     bnss_name = bnssIdToBusinessDict[bnss_key].getName()
#     LABELS = [str(i)+"-"+str(i+1)+" days" for i in range(total_time_slots)]
#     plt.figure(figsize=(20,20))
#     entropy_scores = bnss_statistics[bnss_key][StatConstants.REVIEW_TIME_VELOCITY]
#     plt.title('Review Time Velocity')
#     plt.xlabel('Days')
#     plt.xlim((0,total_time_slots))
#     plt.xticks(range(0,total_time_slots+1), LABELS)
#     plt.ylabel('Review Time Velocity')
#     plt.bar(range(0,len(entropy_scores)),\
#                 entropy_scores,\
#                 label= "bnss")
#     art = []
#     lgd = plt.legend(loc=9, bbox_to_anchor=(0.5, -0.1))
#     art.append(lgd)
#     plt.tight_layout()
#     plt.savefig(join(inputDir, bnss_name+"_velocity")+'.png',\
#                  additional_artists=art,\
#                  bbox_inches="tight")
#     plt.close()

def plotAllOtherMeasures(bnss_statistics, chPtsOutliers, bnssIdToBusinessDict,\
                        bnss_key, total_time_slots, inputDir, clr):
    bnss_name = bnssIdToBusinessDict[bnss_key].getName()

    chPtsOutliersForBnss = dict()

    if bnss_key in chPtsOutliers:
        chPtsOutliersForBnss = chPtsOutliers[bnss_key]

    plot = 1
    plt.figure(figsize=(20,20))
    for measure_key in StatConstants.MEASURES:
        if measure_key not in bnss_statistics[bnss_key]:
            continue
        ax = plt.subplot(len(StatConstants.MEASURES), 1, plot)
        plt.title('Business statistics')
        plt.xlabel('Time in multiples of 2 months')
        plt.xlim((bnss_statistics[bnss_key][StatConstants.FIRST_TIME_KEY],total_time_slots-1))

        step = 1
        if total_time_slots>70:
            step = total_time_slots/100

        plt.xticks(range(bnss_statistics[bnss_key][StatConstants.FIRST_TIME_KEY],total_time_slots, step))
        plt.ylabel(measure_key)
        if measure_key == StatConstants.AVERAGE_RATING:
            plt.ylim((1,5))
            plt.yticks(range(1,6))

        if measure_key == StatConstants.MAX_TEXT_SIMILARITY:
            maxSimilarity = numpy.amax(bnss_statistics[bnss_key][measure_key])
            plt.ylim(ymin = 1,ymax = maxSimilarity+1)
        #print bnss_name, measure_key,bnss_statistics[bnss_key][StatConstants.FIRST_TIME_KEY],bnss_statistics[bnss_key][measure_key],bnss_statistics[bnss_key][measure_key][bnss_statistics[bnss_key][StatConstants.FIRST_TIME_KEY]:]
        ax.plot(range(bnss_statistics[bnss_key][StatConstants.FIRST_TIME_KEY],len(bnss_statistics[bnss_key][measure_key])),\
                bnss_statistics[bnss_key][measure_key][bnss_statistics[bnss_key][StatConstants.FIRST_TIME_KEY]:],\
                clr+'o-',\
                label= "bnss")
                #align="center")

        if measure_key in chPtsOutliersForBnss:
            change_idx = chPtsOutliersForBnss[measure_key]
            for idx in change_idx:
                firstKey = bnss_statistics[bnss_key][StatConstants.FIRST_TIME_KEY]
                idx = firstKey+idx

                print bnss_key, measure_key, idx
                ax.axvline(x=idx,\
                            ymin= bnss_statistics[bnss_key][measure_key][idx]/max(bnss_statistics[bnss_key][measure_key][firstKey:]),\
                            linewidth = 2, color = 'r')

        plot+=1
    art = []
    lgd = plt.legend(loc=9, bbox_to_anchor=(0.5, -0.1))
    art.append(lgd)
    plt.tight_layout()
    imgFile = join(inputDir, bnss_name+"_stat")+'.png'
    print bnss_name+" stats are logged to "+imgFile
    plt.savefig(imgFile,\
                 additional_artists=art,\
                 bbox_inches="tight")
    plt.close()


def plotBnssStatistics(bnss_statistics, chPtsOutliers, bnssIdToBusinessDict,\
                        bnss_key, total_time_slots, inputDir, clr):
    plotAllOtherMeasures(bnss_statistics, chPtsOutliers, bnssIdToBusinessDict, bnss_key, total_time_slots, inputDir, clr)


def plotter(bnssKeySet, bnss_statistics, chPtsOutliers, bnssIdToBusinessDict, total_time_slots, plotDir):
    colors = ['g', 'c', 'b', 'm', 'y', 'k']
    beforePlot = datetime.now()
    for bnssKey in bnssKeySet:
        plotBnssStatistics(bnss_statistics, chPtsOutliers, bnssIdToBusinessDict,\
                                     bnssKey, total_time_slots,\
                                      plotDir, random.choice(colors))
    afterPlot = datetime.now()
    print 'Time taken for Plot:',afterPlot-beforePlot

def plotCurve(a,b):
    #plt.figure(figsize=(20,20))
    plt.title('Plot')
    plt.plot(a,b)
    plt.show()

def plotAny(a):
    plt.title('Plot')
    for i in range(a.size):
        plt.plot(i,a[i],'go-')
    plt.show()


def plotTimeSeries(ax, x, y, label):
    ax.plot(x, y, 'g', label=label, linewidth=1.5)

def plotOutlierScores(ax, x, y):
    ax.plot(x, y, 'r', label='Outlier Scores', linewidth=1.5)

def plotOutlierLine(ax, x):
    ax.axvline(x=x, color='b', linewidth=1.5)

def plotMeasuresForBnss(statistics_for_bnss, chPtsOutliersForBnss, inputDir, toBeUsedMeasures, avg_idxs, timeLength = '1-M'):
    plot = 1
    # firstDateTime = statistics_for_bnss[StatConstants.FIRST_DATE_TIME]
    # total_time_slots = lastTimeKey-firstTimeKey+1

    toBeUsedMeasures = [measure for measure in StatConstants.MEASURE_PRIORITY if measure in toBeUsedMeasures]
    max_algo_len = max([len(StatConstants.MEASURES_CHANGE_DETECTION_ALGO[measure_key])\
                         for measure_key in toBeUsedMeasures ])
    fig = plt.figure(figsize=(20, 20))
    step = 10

    firstTimeKey = statistics_for_bnss[StatConstants.FIRST_TIME_KEY]
    lastTimeKey = statistics_for_bnss[StatConstants.LAST_TIME_KEY]
    firstDimensionValues = range(firstTimeKey, lastTimeKey+1)
    xticks = range(firstTimeKey, lastTimeKey+1, step)

#     f, axarr = plt.subplots(len(toBeUsedMeasures), max_algo_len, sharex=True)

    for measure_key in toBeUsedMeasures:
        if measure_key not in statistics_for_bnss or measure_key == StatConstants.NO_OF_REVIEWS:
            continue
        data = statistics_for_bnss[measure_key][firstTimeKey:lastTimeKey+1]

        if chPtsOutliersForBnss:
            algoList = chPtsOutliersForBnss[measure_key].keys()

            if len(algoList) != max_algo_len and len(algoList) == 1:
                algoList = [algoList[0] for algo_iter in range(max_algo_len)]

            for algo in algoList:
                ax1 = fig.add_subplot(len(toBeUsedMeasures), max_algo_len, plot)
                plt.title(algo)
                plt.xlabel('Date')

                plt.xlim(firstTimeKey, lastTimeKey)
                plt.xticks(xticks)

                plt.ylabel(measure_key)

                if measure_key == StatConstants.AVERAGE_RATING:
                    plt.ylim((1,5))
                    plt.yticks(range(1,6))

                modified_data = data
                if measure_key in [StatConstants.NON_CUM_NO_OF_REVIEWS,
                                   StatConstants.NO_OF_POSITIVE_REVIEWS, StatConstants.NO_OF_NEGATIVE_REVIEWS]:
                    import math
                    modified_data = [d+1 for d in data]
                    ax1.set_yscale('log')

                plotTimeSeries(ax1, firstDimensionValues, modified_data, measure_key)

                chOutlierIdxs, chPtsOutlierScores = chPtsOutliersForBnss[measure_key][algo]
                if len(chPtsOutlierScores) > 0:

                    max_score = -float('inf')
                    min_score = float('inf')

                    for a in algoList:
                        idxs, scs = chPtsOutliersForBnss[measure_key][a]
                        if len(scs) > 0:
                            max_score = max((max_score, max(scs)))
                            min_score = min((min_score, min(scs)))

                    if measure_key in [StatConstants.NON_CUM_NO_OF_REVIEWS,
                                       StatConstants.NO_OF_POSITIVE_REVIEWS,
                                       StatConstants.NO_OF_NEGATIVE_REVIEWS]:
                        max_score += 1
                        min_score += 1

                    ax2 = ax1.twinx()
                    ax2.set_ylim((min_score, max_score+0.01))
                    scores = chPtsOutlierScores
                    if len(scores) > 0:
                        if algo == StatConstants.LOCAL_AR:
                            for idx in sorted(avg_idxs):
                                idx1, idx2 = AnomalyDetector.getRangeIdxs(idx)
                                x = []
                                plot_scores = []
                                for indx in range(idx1, idx2+1):
                                    if indx >= len(scores):
                                        continue
                                    x.append(firstTimeKey+indx)
                                    if measure_key in [StatConstants.NON_CUM_NO_OF_REVIEWS,
                                       StatConstants.NO_OF_POSITIVE_REVIEWS, StatConstants.NO_OF_NEGATIVE_REVIEWS]:
                                        plot_scores.append(scores[indx]+1)
                                        ax2.set_yscale('log')
                                    else:
                                        plot_scores.append(scores[indx])
                                plotOutlierScores(ax2, x, plot_scores)
                        else:
                            if measure_key in [StatConstants.NON_CUM_NO_OF_REVIEWS,
                                       StatConstants.NO_OF_POSITIVE_REVIEWS, StatConstants.NO_OF_NEGATIVE_REVIEWS]:
                                scores = chPtsOutlierScores
                                scores = [scores[indx]+1 for indx in range(len(scores))]
                                ax2.set_yscale('log')
                                plotOutlierScores(ax2, range(firstTimeKey, firstTimeKey+len(scores)), scores)
                            else:
                                plotOutlierScores(ax2, range(firstTimeKey, firstTimeKey+len(chPtsOutlierScores)), chPtsOutlierScores)

                if measure_key not in StatConstants.MEASURE_LEAD_SIGNALS:
                    for idx in sorted(avg_idxs):
                        idx1, idx2 = AnomalyDetector.getRangeIdxs(idx)
                        outlier_idxs = [outlier_idx for outlier_idx in chOutlierIdxs if
                                        outlier_idx < idx2 and idx1 <= outlier_idx < len(chPtsOutlierScores)]
                        if len(outlier_idxs) > 0:
                            outlier_idx = min(outlier_idxs, key= lambda outlier_idx : math.fabs(idx-outlier_idx))
                            plotOutlierLine(ax1, firstDimensionValues[outlier_idx])
                else:
                    for idx in chOutlierIdxs:
                        plotOutlierLine(ax1, firstDimensionValues[idx])
                plot += 1
        else:
            ax1 = fig.add_subplot(len(toBeUsedMeasures), 1, plot)
            plt.title(algo)
            plt.xlabel('Date')

            plt.xlim(firstTimeKey, lastTimeKey)
            plt.xticks(xticks)

            plt.ylabel(measure_key)

            if measure_key == StatConstants.AVERAGE_RATING:
                plt.ylim((1,5))
                plt.yticks(range(1,6))

            plotTimeSeries(ax1, firstDimensionValues, data, measure_key)

            chOutlierIdxs, chPtsOutlierScores = [], []
            if len(chPtsOutlierScores) > 0:
                ax2 = ax1.twinx()
                plotOutlierScores(ax2, range(firstTimeKey, firstTimeKey+len(chPtsOutlierScores)),
                                  chPtsOutlierScores)

            for idx in chOutlierIdxs:
                plotOutlierLine(ax1, firstDimensionValues[idx])

    art = []
    plt.tight_layout()

    imgFile = join(inputDir, statistics_for_bnss[StatConstants.BNSS_ID]+"_stat")+'.png'

    print statistics_for_bnss[StatConstants.BNSS_ID]+" stats are logged to "+imgFile

    plt.savefig(imgFile,\
                 additional_artists=art,\
                 bbox_inches="tight")
    plt.close()