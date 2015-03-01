__author__ = 'santhosh'
import csv
from datetime import datetime
import networkx
import numpy
import os
from os.path import join
import sys

from itunes_utils.ItunesDataReader import ItunesDataReader
import matplotlib.pyplot as plt
from temporal_statistics import measure_extractor
from util import SIAUtil, PlotUtil, GraphUtil, StatConstants
from util.GraphUtil import SuperGraph, TemporalGraph
from anomaly_detection import AnomalyDetector

import changefinder

def tryChangeFinderOnProductDimensions():

    csvFolder = '/media/santhosh/Data/workspace/datalab/data/Itunes'

    rdr = ItunesDataReader()
    (usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict) = rdr.readData(csvFolder)

    timeLength = '1-M'

    superGraph,cross_time_graphs = GraphUtil.createGraphs(usrIdToUserDict,\
                                                           bnssIdToBusinessDict,\
                                                            reviewIdToReviewsDict, timeLength)

    plotDir =  join(join(csvFolder, os.pardir), 'latest')

    bnssKeys = [bnss_key for bnss_key,bnss_type in superGraph.nodes()\
                 if bnss_type == SIAUtil.PRODUCT]

    bnssKeys = sorted(bnssKeys, reverse=True, key = lambda x: len(superGraph.neighbors((x,SIAUtil.PRODUCT))))

    bnssKeySet = set(bnssKeys[:1])

    bnss_statistics = measure_extractor.extractMeasures(usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict,\
                     superGraph, cross_time_graphs, plotDir, bnssKeySet, timeLength)

    chPtsOutliers = AnomalyDetector.detectChPtsAndOutliers(bnss_statistics)

    total_time_slots = len(cross_time_graphs.keys())

    for bnssKey in bnssKeySet:
        plotMeasures( bnss_statistics, chPtsOutliers,\
                          bnssIdToBusinessDict, bnssKey, total_time_slots, plotDir)


def plotMeasures(bnss_statistics, chPtsOutliers, bnssIdToBusinessDict,\
                        bnss_key, total_time_slots, inputDir):

    bnss_name = bnssIdToBusinessDict[bnss_key].getName()

    toBeUsedMeasures = [StatConstants.AVERAGE_RATING, StatConstants.RATING_ENTROPY]

    plot = 1

    plt.figure(figsize=(20,20))

    for measure_key in toBeUsedMeasures:
        if measure_key not in bnss_statistics[bnss_key]:
            continue

        firstTimeKey = bnss_statistics[bnss_key][StatConstants.FIRST_TIME_KEY]

        step = 1
        if total_time_slots>70:
            step = total_time_slots/100

        plt.title('Business statistics')
        plt.xlabel('Time in multiples of 1 months')
        plt.xlim((firstTimeKey,total_time_slots-1))
        plt.xticks(range(firstTimeKey,total_time_slots, step))

        ax1 = plt.subplot(len(toBeUsedMeasures)*2, 1, plot)


        plt.ylabel(measure_key)

        if measure_key == StatConstants.AVERAGE_RATING:
            plt.ylim((1,5))
            plt.yticks(range(1,6))

        ax1.plot(range(firstTimeKey,len(bnss_statistics[bnss_key][measure_key])),\
                bnss_statistics[bnss_key][measure_key][firstTimeKey:],\
                'g'+'o-',\
                label= "bnss")
                #align="center")

        plot+=1

        ax2 = plt.subplot(len(toBeUsedMeasures)*2, 1, plot)


        ax2.plot(range(firstTimeKey,len(bnss_statistics[bnss_key][measure_key])),\
                chPtsOutliers[bnss_key][measure_key][firstTimeKey:],\
                'b'+'o-',\
                label= "bnss")

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


tryChangeFinderOnProductDimensions()