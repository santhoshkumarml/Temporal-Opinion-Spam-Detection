__author__ = 'santhosh'
import os
from os.path import join
import sys

from itunes_utils.ItunesDataReader import ItunesDataReader
import matplotlib.pyplot as plt
from temporal_statistics import measure_extractor
from util import SIAUtil, PlotUtil, GraphUtil, StatConstants
from anomaly_detection import AnomalyDetector
import scipy
import numpy
from datetime import datetime

import changefinder


def generateStatsAndPlots(bnssIdToBusinessDict, bnssKeySet, cross_time_graphs, plotDir, reviewIdToReviewsDict,
                          superGraph, timeLength, toBeUsedMeasures, total_time_slots, usrIdToUserDict):
    bnss_statistics = measure_extractor.extractMeasures(usrIdToUserDict, bnssIdToBusinessDict, reviewIdToReviewsDict, \
                                                        superGraph, cross_time_graphs, plotDir, bnssKeySet, timeLength,
                                                        toBeUsedMeasures)
    for bnssKey in bnssKeySet:
        firstTimeKey = bnss_statistics[bnssKey][StatConstants.FIRST_TIME_KEY]
        print 'No Of Reviews'
        print bnss_statistics[bnssKey][StatConstants.NO_OF_REVIEWS][firstTimeKey:]
    chPtsOutliers = AnomalyDetector.detectChPtsAndOutliers(bnss_statistics)
    beforePlot = datetime.now()
    for bnssKey in bnssKeySet:
        plotMeasures(bnss_statistics, chPtsOutliers, \
                     bnssIdToBusinessDict, bnssKey, total_time_slots, plotDir, toBeUsedMeasures)
    afterPlot = datetime.now()
    print 'Time taken for plot', afterPlot - beforePlot


def tryChangeFinderOnProductDimensions():

    csvFolder = '/media/santhosh/Data/workspace/datalab/data/Itunes'

    rdr = ItunesDataReader()
    (usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict) = rdr.readData(csvFolder)

    timeLength = '1-M'

    superGraph,cross_time_graphs = GraphUtil.createGraphs(usrIdToUserDict,\
                                                           bnssIdToBusinessDict,\
                                                            reviewIdToReviewsDict, timeLength)

    plotDir =  join(join(csvFolder, os.pardir), 'latest')

    # bnssKeys = ['432306789', '412629178', '402688503', '456280861',\
    #             '284819997', '405862075', '289190113', '312575632',\
    #             '404593641', '364873934']
    #bnssKeys = ['284819997']

    bnssKeys = [bnss_key for bnss_key,bnss_type in superGraph.nodes()\
                 if bnss_type == SIAUtil.PRODUCT]

    bnssKeys = ['284417350']

    bnssKeys = sorted(bnssKeys, reverse=True, key = lambda x: len(superGraph.neighbors((x,SIAUtil.PRODUCT))))

    start = 0
    end = 1
    bnssKeys = bnssKeys[start:end]

    toBeUsedMeasures = set([StatConstants.AVERAGE_RATING, StatConstants.ENTROPY_SCORE, StatConstants.NO_OF_REVIEWS])
    maxText = set([StatConstants.MAX_TEXT_SIMILARITY])
    toBeUsedMeasures = set(StatConstants.MEASURES) - maxText

    for i in range(1,end-start+1):
        bnssKeySet = set(bnssKeys[i-1:i])
        total_time_slots = len(cross_time_graphs.keys())
        generateStatsAndPlots(bnssIdToBusinessDict, bnssKeySet, cross_time_graphs, plotDir, reviewIdToReviewsDict,
                              superGraph, timeLength, toBeUsedMeasures, total_time_slots, usrIdToUserDict)

def plotMeasures(bnss_statistics, chPtsOutliers, bnssIdToBusinessDict,\
                        bnss_key, total_time_slots, inputDir, toBeUsedMeasures):

    bnss_name = bnssIdToBusinessDict[bnss_key].getName()

    plot = 1

    fig = plt.figure(figsize=(20,20))

    for measure_key in toBeUsedMeasures:
        if measure_key not in bnss_statistics[bnss_key]:
            continue

        firstTimeKey = bnss_statistics[bnss_key][StatConstants.FIRST_TIME_KEY]

        step = 1

        if total_time_slots>50:
            step = total_time_slots/100

        ax1 = fig.add_subplot(len(toBeUsedMeasures), 1, plot)

        plt.title('Business statistics')
        plt.xlabel('Time in multiples of 1 months')

        plt.xlim((firstTimeKey,total_time_slots-1))
        plt.xticks(range(firstTimeKey,total_time_slots, step))

        plt.ylabel(measure_key)

        if measure_key == StatConstants.AVERAGE_RATING:
            plt.ylim((1,5))
            plt.yticks(range(1,6))

        ax1.plot(range(firstTimeKey,len(bnss_statistics[bnss_key][measure_key])),\
                bnss_statistics[bnss_key][measure_key][firstTimeKey:], 'g', label = 'bnss')
                #align="center")

        chOutlierScores = chPtsOutliers[bnss_key][measure_key]

        idxs = None

        if measure_key == StatConstants.AVERAGE_RATING:
            ta, tai, taf, amp = chOutlierScores
            idxs = ta
        else:
            ax2 = ax1.twinx()
            ax2.plot(range(firstTimeKey,len(bnss_statistics[bnss_key][measure_key])),\
                 chOutlierScores, 'r', label = 'bnss')
            result = scipy.signal.argrelextrema(numpy.array(chOutlierScores), numpy.greater)
            idxs = result[0]

        idxs = [idx+firstTimeKey for idx in idxs]

        for idx in idxs:
            ax1.axvline(x=idx,linewidth=2, color='r')

        plot += 1

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


tryChangeFinderOnProductDimensions()
