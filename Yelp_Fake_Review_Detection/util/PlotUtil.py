'''
Created on Jan 10, 2015

@author: Santhosh
'''

import matplotlib.pyplot as plt
from os.path import join
from util import StatConstants
import numpy

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

def plotAllOtherMeasures(bnss_statistics, bnssIdToBusinessDict,\
                        bnss_key, total_time_slots, inputDir, clr):
    bnss_name = bnssIdToBusinessDict[bnss_key].getName()
    plot = 1
    plt.figure(figsize=(20,20))
    for measure_key in StatConstants.MEASURES:
        if measure_key not in bnss_statistics[bnss_key]:
            continue
        plt.subplot(len(StatConstants.MEASURES), 1, plot)
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
        plt.plot(range(bnss_statistics[bnss_key][StatConstants.FIRST_TIME_KEY],len(bnss_statistics[bnss_key][measure_key])),\
                bnss_statistics[bnss_key][measure_key][bnss_statistics[bnss_key][StatConstants.FIRST_TIME_KEY]:],\
                clr+'o-',\
                label= "bnss")
                #align="center")
        plot+=1
    art = []
    lgd = plt.legend(loc=9, bbox_to_anchor=(0.5, -0.1))
    art.append(lgd)
    plt.tight_layout()
    plt.savefig(join(inputDir, bnss_name+"_stat")+'.png',\
                 additional_artists=art,\
                 bbox_inches="tight")
    plt.close()
        
def plotBnssStatistics(bnss_statistics, bnssIdToBusinessDict,\
                        bnss_key, total_time_slots, inputDir, clr):
    plotAllOtherMeasures(bnss_statistics, bnssIdToBusinessDict, bnss_key, total_time_slots, inputDir, clr)

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
