'''
Created on Dec 29, 2014

@author: santhosh
'''
from datetime import datetime,timedelta
import math
import numpy
import random
import sys


import matplotlib.pyplot as plt
from util import SIAUtil
from util.ScrappedDataReader import ScrappedDataReader

FIRST_TIME_KEY = 'First Time Key'

AVERAGE_RATING = 'Average Rating'
RATING_ENTROPY = 'Rating entropy'
NO_OF_REVIEWS = 'Number of Reviews'
RATIO_OF_SINGLETONS = 'Ratio of Singletons'
RATIO_OF_FIRST_TIMERS = 'Ratio of First-timers'
YOUTH_SCORE = 'Youth Score'
ENTROPY_SCORE = 'Entropy Score'
RATING_DISTRIBUTION = 'Rating Distribution'
MAX_TEXT_SIMILARITY = 'Max Text Similarity'
MEASURES = [AVERAGE_RATING, RATING_ENTROPY, NO_OF_REVIEWS, RATIO_OF_SINGLETONS, RATIO_OF_FIRST_TIMERS, YOUTH_SCORE,\
            ENTROPY_SCORE, MAX_TEXT_SIMILARITY]

def sigmoid_prime(x):
    return (2.0/(1+math.exp(-x)))-1

def entropyFn(probability_dict):
    entropy = 0
    for key in probability_dict:
        probability = probability_dict[key]
        if probability > 0:
            entropy += -(probability*math.log(probability,2))
    return entropy
    
def generateStatistics(superGraph, cross_time_graphs, usrIdToUserDict, bnssIdToBusinessDict, reviewIdToReviewsDict):
    bnss_statistics = dict()
    total_time_slots = len(cross_time_graphs.keys())
    
    for timeKey in cross_time_graphs.iterkeys():
        G = cross_time_graphs[timeKey]
        for bnssId in G.getBusinessIds():
            if bnssId not in bnss_statistics:
                bnss_statistics[bnssId] = dict()
                bnss_statistics[bnssId][FIRST_TIME_KEY] = timeKey
            bnss_name = bnssIdToBusinessDict[bnssId].getName()
            #Average Rating
            if AVERAGE_RATING not in bnss_statistics[bnssId]:
                bnss_statistics[bnssId][AVERAGE_RATING] = numpy.zeros(total_time_slots)
                
            neighboring_usr_nodes = G.neighbors((bnssId,SIAUtil.PRODUCT))
            reviews_for_bnss = []
            for (usrId, usr_type) in neighboring_usr_nodes:
                review_for_bnss = G.getReview(usrId,bnssId)
                reviews_for_bnss.append(review_for_bnss)
            ratings = [review.getRating() for review in reviews_for_bnss]
            bnss_statistics[bnssId][AVERAGE_RATING][timeKey] = float(sum(ratings))
            
            #Rating Entropy
            sorted_rating_list = set(sorted(ratings))
            if RATING_DISTRIBUTION not in bnss_statistics[bnssId]:
                bnss_statistics[bnssId][RATING_DISTRIBUTION] = dict()
                
            if timeKey not in bnss_statistics[bnssId][RATING_DISTRIBUTION]:
                bnss_statistics[bnssId][RATING_DISTRIBUTION][timeKey] = {key:0.0 for key in sorted_rating_list}
            
            for rating in ratings:
                bnss_statistics[bnssId][RATING_DISTRIBUTION][timeKey][rating] += 1.0
            
            for rating in sorted_rating_list:
                bnss_statistics[bnssId][RATING_DISTRIBUTION][timeKey][rating] /= float(len(reviews_for_bnss)) 
              
            #NumberOfReviews
            if NO_OF_REVIEWS not in bnss_statistics[bnssId]: 
                bnss_statistics[bnssId][NO_OF_REVIEWS] = numpy.zeros(total_time_slots)
            noOfReviews = len(neighboring_usr_nodes)
            bnss_statistics[bnssId][NO_OF_REVIEWS][timeKey] = noOfReviews
            
            #Ratio of Singletons
            if RATIO_OF_SINGLETONS not in bnss_statistics[bnssId]: 
                bnss_statistics[bnssId][RATIO_OF_SINGLETONS] = numpy.zeros(total_time_slots)
            noOfSingleTons = 0
            for neighbor in neighboring_usr_nodes:
                if len(superGraph.neighbors(neighbor)) == 1:
                    noOfSingleTons+=1
            bnss_statistics[bnssId][RATIO_OF_SINGLETONS][timeKey] = float(noOfSingleTons)/float(len(reviews_for_bnss))        
            
            #Ratio of First Timers
            if RATIO_OF_FIRST_TIMERS not in bnss_statistics[bnssId]: 
                bnss_statistics[bnssId][RATIO_OF_FIRST_TIMERS] = numpy.zeros(total_time_slots)
            noOfFirstTimers = 0
            for usr_neighbor in neighboring_usr_nodes:
                (usrId, usr_type) = usr_neighbor
                current_temporal_review = G.getReview(usrId, bnssId)
                allReviews = [superGraph.getReview(usrId, super_graph_bnssId) \
                              for (super_graph_bnssId, super_graph_bnss_type) in superGraph.neighbors(usr_neighbor)]
                firstReview = min(allReviews, key= lambda x: SIAUtil.getDateForReview(x))
                if firstReview.getId() == current_temporal_review.getId():
                    noOfFirstTimers+=1
            bnss_statistics[bnssId][RATIO_OF_FIRST_TIMERS][timeKey] = float(noOfFirstTimers)/float(len(reviews_for_bnss))
            
            #Youth Score
            if YOUTH_SCORE not in bnss_statistics[bnssId]: 
                bnss_statistics[bnssId][YOUTH_SCORE] = numpy.zeros(total_time_slots)
            youth_scores = []
            for usr_neighbor in neighboring_usr_nodes:
                (usrId, usr_type) = usr_neighbor
                allReviews = [superGraph.getReview(usrId, super_graph_bnssId) \
                              for (super_graph_bnssId, super_graph_bnss_type) in superGraph.neighbors(usr_neighbor)]
                allReviews = sorted(allReviews, key= lambda x: SIAUtil.getDateForReview(x))
                current_temporal_review = G.getReview(usrId, bnssId)
                reviewAge = (SIAUtil.getDateForReview(current_temporal_review)-SIAUtil.getDateForReview(allReviews[0])).days
                youth_score = 1-sigmoid_prime(reviewAge)
                youth_scores.append(youth_score)
            bnss_statistics[bnssId][YOUTH_SCORE][timeKey] = numpy.mean(numpy.array(youth_scores))
            
            #Entropy Score
            
            #Max Text Similarity
    
    
    #POST PROCESSING FOR REVIEW AVERAGE_RATING, NO_OF_REVIEWS, RATING_ENTROPY and ENTROPY_SCORE
    for bnss_key in bnss_statistics:
        statistics_for_bnss = bnss_statistics[bnss_key]
        no_of_reviews_for_bnss = statistics_for_bnss[NO_OF_REVIEWS]
        
        statistics_for_bnss[ENTROPY_SCORE] = numpy.zeros(total_time_slots)
        entropy_score = statistics_for_bnss[ENTROPY_SCORE] 

        bnss_node = (bnss_key,SIAUtil.PRODUCT)
        allReviews = [superGraph.getReview(usr_neighbor[0], bnss_key)\
                       for usr_neighbor in superGraph.neighbors(bnss_node)]
        allReviews = sorted(allReviews, key = lambda x: SIAUtil.getDateForReview(x))
        allReviewVelocity = [ (SIAUtil.getDateForReview(allReviews[x+1])-SIAUtil.getDateForReview(allReviews[x])).days \
                             for x in range(len(allReviews)-1)]
        print len(allReviews), len(allReviewVelocity)
        
            
#         for timeKey in range(total_time_slots):
#             rating_sum_for_bnss[timeKey] = no_of_reviews_for_bnss[timeKey]*avg_rating_for_bnss[timeKey]
#             
#         if bnssIdToBusinessDict[bnss_key].getName() == 'Arizona Humane Society':
#             print statistics_for_bnss[NO_OF_REVIEWS],statistics_for_bnss[AVERAGE_RATING]
            
        for timeKey in range(total_time_slots):
            if timeKey > 0:
                #POST PROCESSING FOR NUMBER_OF_REVIEWS
                statistics_for_bnss[NO_OF_REVIEWS][timeKey] = no_of_reviews_for_bnss[timeKey-1]+no_of_reviews_for_bnss[timeKey]
                #POST PROCESSING FOR AVERAGE RATING
                if no_of_reviews_for_bnss[timeKey] > 0:
                    sum_of_ratings = (statistics_for_bnss[AVERAGE_RATING][timeKey-1]*no_of_reviews_for_bnss[timeKey-1])
                    sum_of_ratings += statistics_for_bnss[AVERAGE_RATING][timeKey]
                    statistics_for_bnss[AVERAGE_RATING][timeKey] = sum_of_ratings/no_of_reviews_for_bnss[timeKey]
                else:
                    statistics_for_bnss[AVERAGE_RATING][timeKey] = 0
            else:
                if no_of_reviews_for_bnss[timeKey] > 0:
                    statistics_for_bnss[AVERAGE_RATING][timeKey] /=  statistics_for_bnss[NO_OF_REVIEWS][timeKey]
            
            #POST PROCESSING FOR RATING ENTROPY
            if timeKey in statistics_for_bnss[RATING_DISTRIBUTION]:
                entropy = entropyFn(statistics_for_bnss[RATING_DISTRIBUTION][timeKey])
                if RATING_ENTROPY not in statistics_for_bnss:
                    statistics_for_bnss[RATING_ENTROPY] = numpy.zeros(total_time_slots)
                statistics_for_bnss[RATING_ENTROPY][timeKey] = entropy
                
#         if bnssIdToBusinessDict[bnss_key].getName() == 'Matsuhisa':               
#         if bnssIdToBusinessDict[bnss_key].getName() == 'Arizona Humane Society':
#             print statistics_for_bnss[NO_OF_REVIEWS],statistics_for_bnss[AVERAGE_RATING]
            
    return bnss_statistics


def plotBnssStatistics(bnss_statistics, bnssIdToBusinessDict, bnss_key, total_time_slots, clr):
    bnss_name = bnssIdToBusinessDict[bnss_key].getName()
    plot = 1
    plt.figure(figsize=(20,20))

    LABELS = [str(i)+"-"+str(i+1)+" days" for i in range(total_time_slots)]
    
    for measure_key in MEASURES:
        if measure_key not in bnss_statistics[bnss_key]:
            continue
        plt.subplot(len(MEASURES), 1, plot)
        plt.title('Business statistics')
        plt.xlabel('Time in multiples of 2 months')
        plt.xlim((bnss_statistics[bnss_key][FIRST_TIME_KEY],total_time_slots))
        plt.xticks(range(bnss_statistics[bnss_key][FIRST_TIME_KEY],total_time_slots+1))
        plt.ylabel(measure_key)
        if measure_key == AVERAGE_RATING:
            plt.ylim((1,5))
            plt.yticks(range(1,6))
        #print measure_key,bnss_statistics[bnss_key][FIRST_TIME_KEY],bnss_statistics[bnss_key][measure_key],bnss_statistics[bnss_key][measure_key][bnss_statistics[bnss_key][FIRST_TIME_KEY]+1:]
        plt.plot(range(bnss_statistics[bnss_key][FIRST_TIME_KEY],len(bnss_statistics[bnss_key][measure_key])),\
                bnss_statistics[bnss_key][measure_key][bnss_statistics[bnss_key][FIRST_TIME_KEY]:],\
                clr+'o-',\
                label= "bnss")
                #align="center")
        plot+=1
    art = []
    lgd = plt.legend(loc=9, bbox_to_anchor=(0.5, -0.1))
    art.append(lgd)
    plt.tight_layout()
    plt.savefig('/media/santhosh/Data/workspace/datalab/data/latest/'+bnss_name+'.png',\
                 additional_artists=art,\
                 bbox_inches="tight")
    plt.close()
        

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python temporal_statistics.py fileName'
        sys.exit()
    inputFileName = sys.argv[1]
    
    beforeGraphPopulationTime = datetime.now()
    #(usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict) = dataReader.parseAndCreateObjects(inputFileName)
    
    rdr = ScrappedDataReader()
    
    (usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict) = rdr.readData(inputFileName)
    superGraph = SuperGraph.createGraph(usrIdToUserDict,\
                                             bnssIdToBusinessDict,\
                                             reviewIdToReviewsDict)
    
    cross_time_graphs = TemporalGraph.createTemporalGraph(usrIdToUserDict,\
                                             bnssIdToBusinessDict,\
                                             reviewIdToReviewsDict,\
                                             '2-M', False)
    bnss_statistics = generateStatistics(superGraph, cross_time_graphs, usrIdToUserDict, bnssIdToBusinessDict, reviewIdToReviewsDict)
    sys.exit()
    
    bnssKeys = [bnss_key for bnss_key in bnss_statistics]
    
    bnssKeys = sorted(bnssKeys, reverse=True, key = lambda x: len(superGraph.neighbors((x,SIAUtil.PRODUCT))))
    
    colors = ['g', 'c', 'r', 'b', 'm', 'y', 'k']
    i=0
    while i<100:
        plotBnssStatistics(bnss_statistics, bnssIdToBusinessDict, bnssKeys[i],len(cross_time_graphs.keys()), random.choice(colors))
        i+=1