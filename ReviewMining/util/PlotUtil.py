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


def plotMeasuresForBnss(statistics_for_bnss, chPtsOutliersForBnss, inputDir, toBeUsedMeasures, timeLength = '1-M'):

    plot = 1

    fig = plt.figure(figsize=(20,20))

    avg_idxs = None

    total_time_slots = len(statistics_for_bnss[StatConstants.AVERAGE_RATING])

    step = 3

        # if total_time_slots > 50:
        #     step = total_time_slots/50
        #
        # step = 3

    years   = mdates.YearLocator()   # every year
    months  = mdates.MonthLocator()  # every month
    days = mdates.DayLocator()
    daysFmt = mdates.DateFormatter('%b-%Y')


    for measure_key in toBeUsedMeasures:
        if measure_key not in statistics_for_bnss:
            continue
        firstTimeKey = statistics_for_bnss[StatConstants.FIRST_TIME_KEY]
        firstDateTime = statistics_for_bnss[StatConstants.FIRST_DATE_TIME]
        firstDimensionValues = range(firstTimeKey, total_time_slots)
        xticks = range(firstTimeKey, total_time_slots, step)
        # firstDimensionValues = GraphUtil.getDates(firstDateTime, range(firstTimeKey, total_time_slots), timeLength)
        # xticks = GraphUtil.getDates(firstDateTime, range(firstTimeKey, total_time_slots, step), timeLength)

        ax1 = fig.add_subplot(len(toBeUsedMeasures), 1, plot)

        plt.title('Business statistics')
        plt.xlabel('Date')

        plt.xlim(firstDimensionValues[0], firstDimensionValues[-1])
        plt.xticks(xticks)

        plt.ylabel(measure_key)

        #ax1.xaxis.set_major_formatter(daysFmt)

        if measure_key == StatConstants.AVERAGE_RATING:
            plt.ylim((1,5))
            plt.yticks(range(1,6))

        ax1.plot(firstDimensionValues,\
                statistics_for_bnss[measure_key][firstTimeKey:], 'g', label=measure_key)

        chOutlierIdxs, chPtsOutlierScores = chPtsOutliersForBnss[measure_key]

        if len(chPtsOutlierScores) > 0:
            ax2 = ax1.twinx()
            ax2.plot(firstDimensionValues, chPtsOutlierScores, 'r', label='Outlier Scores')

        for idx in chOutlierIdxs:
            ax1.axvline(x=firstDimensionValues[idx], linewidth=2, color='r')

        plot += 1

    art = []
    lgd = plt.legend(loc=9, bbox_to_anchor=(0.5, -0.1))
    art.append(lgd)
    #fig.autofmt_xdate()
    plt.tight_layout()

    imgFile = join(inputDir, statistics_for_bnss[StatConstants.BNSS_ID]+"_stat")+'.png'

    print statistics_for_bnss[StatConstants.BNSS_ID]+" stats are logged to "+imgFile

    plt.savefig(imgFile,\
                 additional_artists=art,\
                 bbox_inches="tight")
    plt.close()