'''
Created on Jan 10, 2015

@author: Santhosh
'''

import matplotlib.pyplot as plt
from os.path import join
from util import StatConstants

def plotEntropyScore(bnss_statistics, bnssIdToBusinessDict,\
                        bnss_key, total_time_slots, inputDir, clr):
    
    bnss_name = bnssIdToBusinessDict[bnss_key].getName()
    LABELS = [str(i)+"-"+str(i+1)+" days" for i in range(total_time_slots)]
    plt.figure(figsize=(20,20))
    entropy_scores = bnss_statistics[bnss_key][StatConstants.ENTROPY_SCORE]
    plt.title('Review Time Velocity')
    plt.xlabel('Days')
    plt.xlim((0,total_time_slots))
    plt.xticks(range(0,total_time_slots+1), LABELS)
    plt.ylabel('Review Time Velocity')
    plt.bar(range(0,len(bnss_statistics[bnss_key][StatConstants.ENTROPY_SCORE])),\
                entropy_scores,\
                label= "bnss")
    art = []
    lgd = plt.legend(loc=9, bbox_to_anchor=(0.5, -0.1))
    art.append(lgd)
    plt.tight_layout()
    plt.savefig(join(inputDir, bnss_name+"_velocity")+'.png',\
                 additional_artists=art,\
                 bbox_inches="tight")
    plt.close()
    
def plotBnssStatistics(bnss_statistics, bnssIdToBusinessDict,\
                        bnss_key, total_time_slots, inputDir, clr):
    bnss_name = bnssIdToBusinessDict[bnss_key].getName()
    plotEntropyScore(bnss_statistics, bnssIdToBusinessDict, bnss_key, total_time_slots, inputDir, clr)
    plot = 1
    plt.figure(figsize=(20,20))
    for measure_key in StatConstants.MEASURES:
        if measure_key not in bnss_statistics[bnss_key] or measure_key == StatConstants.ENTROPY_SCORE:
            continue
        plt.subplot(len(StatConstants.MEASURES), 1, plot)
        plt.title('Business statistics')
        plt.xlabel('Time in multiples of 2 months')
        plt.xlim((bnss_statistics[bnss_key][StatConstants.FIRST_TIME_KEY],total_time_slots))
        plt.xticks(range(bnss_statistics[bnss_key][StatConstants.FIRST_TIME_KEY],total_time_slots+1))
        plt.ylabel(measure_key)
        if measure_key == StatConstants.AVERAGE_RATING:
            plt.ylim((1,5))
            plt.yticks(range(1,6))
        #print measure_key,bnss_statistics[bnss_key][FIRST_TIME_KEY],bnss_statistics[bnss_key][measure_key],bnss_statistics[bnss_key][measure_key][bnss_statistics[bnss_key][FIRST_TIME_KEY]+1:]
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