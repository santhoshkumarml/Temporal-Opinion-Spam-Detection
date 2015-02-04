'''
Created on Dec 29, 2014

@author: santhosh
'''
from datetime import datetime
import math
import numpy
import os
from os.path import join
import random
import sys
from util import PlotUtil, GraphUtil
from util import SIAUtil
from util import StatConstants
from util.GraphUtil import SuperGraph, TemporalGraph
from util.ScrappedDataReader import ScrappedDataReader
from intervaltree import IntervalTree
from lsh import ShingleUtil

timeLength = '1-W'

def printSimilarReviews(bin_count, candidateGroups, timeKey, bnss_key, reviewTextsInThisTimeBlock):
    bucketNumbers = set([i for i in range(len(bin_count)) if bin_count[i]>1])
    bucketIndexListPair = []
    for bucketNumber in bucketNumbers:
        indexes = [i for i in range(len(candidateGroups)) if candidateGroups[i]==bucketNumber]
        bucketIndexListPair.append((bucketNumber,indexes))
    print bnss_key, timeKey
    for bucketNumber,indexes in bucketIndexListPair:
        print '-------------------------'
        print bucketNumber
        for index in indexes:
            print reviewTextsInThisTimeBlock[index]
        print '-------------------------'
        
def sigmoid_prime(x):
    return (2.0/(1+math.exp(-x)))-1

def entropyFn(probability_dict):
    entropy = 0
    for key in probability_dict:
        probability = probability_dict[key]
        if probability > 0:
            entropy += -(probability*math.log(probability,2))
    return entropy

def constructIntervalTree(days):
    t = IntervalTree()
    end = days
    t[0:1] = 0
    iter_start = 1
    step_index = 0
    while(iter_start<end):
        iterend = iter_start+(2**step_index)
        t[iter_start:iterend] = 0
        iter_start =  iterend
        step_index+=1
    return t


def getBucketIntervalForBucketTree(bucketTree, point):
    bucket_intervals = list(bucketTree[point])
    assert len(bucket_intervals) == 1
    return bucket_intervals[0]

def updateBucketTree(bucketTree, point):
    interval = getBucketIntervalForBucketTree(bucketTree, point)
    begin,end,data = interval
    bucketTree.remove(interval)
    bucketTree[begin:end] = data + 1.0
    

def fixZeroReviewTimeStamps(timeKey, statistics_for_bnss):
#     changed = False
    noOfReviewsInTime = statistics_for_bnss[StatConstants.NO_OF_REVIEWS][timeKey]
    for measure_key in StatConstants.MEASURES:
        if measure_key != StatConstants.NO_OF_REVIEWS and measure_key != StatConstants.AVERAGE_RATING:
            if noOfReviewsInTime == 0:
                statistics_for_bnss[measure_key][timeKey] = statistics_for_bnss[measure_key][timeKey - 1]
#                 changed = True
#     if changed:
#         print timeKey
#         print statistics_for_bnss

def generateStatistics(superGraph, cross_time_graphs,\
                        usrIdToUserDict, bnssIdToBusinessDict,\
                         reviewIdToReviewsDict, bnssKeys):
    bnss_statistics = dict()
    total_time_slots = len(cross_time_graphs.keys())
    
    for timeKey in cross_time_graphs.iterkeys():
        print timeKey
        G = cross_time_graphs[timeKey]
        for bnssId in G.getBusinessIds():
            if bnssId not in bnssKeys:
                continue
            
            if bnssId not in bnss_statistics:
                bnss_statistics[bnssId] = dict()
                bnss_statistics[bnssId][StatConstants.FIRST_TIME_KEY] = timeKey
                    
            bnss_name = bnssIdToBusinessDict[bnssId].getName()
            
            neighboring_usr_nodes = G.neighbors((bnssId,SIAUtil.PRODUCT))
            #Average Rating
            if StatConstants.AVERAGE_RATING not in bnss_statistics[bnssId]:
                bnss_statistics[bnssId][StatConstants.AVERAGE_RATING] = numpy.zeros(total_time_slots)
            
            reviews_for_bnss = []
            
            for (usrId, usr_type) in neighboring_usr_nodes:
                review_for_bnss = G.getReview(usrId,bnssId)
                reviews_for_bnss.append(review_for_bnss)
            ratings = [review.getRating() for review in reviews_for_bnss]
            bnss_statistics[bnssId][StatConstants.AVERAGE_RATING][timeKey] = float(sum(ratings))
            
            #Rating Entropy
            sorted_rating_list = set(sorted(ratings))
            if StatConstants.RATING_DISTRIBUTION not in bnss_statistics[bnssId]:
                bnss_statistics[bnssId][StatConstants.RATING_DISTRIBUTION] = dict()
                
            if StatConstants.RATING_ENTROPY not in bnss_statistics[bnssId]:
                    bnss_statistics[bnssId][StatConstants.RATING_ENTROPY] = numpy.zeros(total_time_slots)
                
            if timeKey not in bnss_statistics[bnssId][StatConstants.RATING_DISTRIBUTION]:
                bnss_statistics[bnssId][StatConstants.RATING_DISTRIBUTION][timeKey] = {key:0.0 for key in sorted_rating_list}
            
            for rating in ratings:
                bnss_statistics[bnssId][StatConstants.RATING_DISTRIBUTION][timeKey][rating] += 1.0
            
            for rating in sorted_rating_list:
                bnss_statistics[bnssId][StatConstants.RATING_DISTRIBUTION][timeKey][rating] /= float(len(reviews_for_bnss)) 
            
            
            #NumberOfReviews
            if StatConstants.NO_OF_REVIEWS not in bnss_statistics[bnssId]: 
                bnss_statistics[bnssId][StatConstants.NO_OF_REVIEWS] = numpy.zeros(total_time_slots)
                
            noOfReviews = len(neighboring_usr_nodes)
            bnss_statistics[bnssId][StatConstants.NO_OF_REVIEWS][timeKey] = noOfReviews
            
            #Ratio of Singletons
            if StatConstants.RATIO_OF_SINGLETONS not in bnss_statistics[bnssId]: 
                bnss_statistics[bnssId][StatConstants.RATIO_OF_SINGLETONS] = numpy.zeros(total_time_slots)
                
            noOfSingleTons = 0
            for neighbor in neighboring_usr_nodes:
                if len(superGraph.neighbors(neighbor)) == 1:
                    noOfSingleTons+=1
                    
            bnss_statistics[bnssId][StatConstants.RATIO_OF_SINGLETONS][timeKey] = float(noOfSingleTons)/float(len(reviews_for_bnss))        
            
            #Ratio of First Timers
            if StatConstants.RATIO_OF_FIRST_TIMERS not in bnss_statistics[bnssId]: 
                bnss_statistics[bnssId][StatConstants.RATIO_OF_FIRST_TIMERS] = numpy.zeros(total_time_slots)
                
            noOfFirstTimers = 0
            for usr_neighbor in neighboring_usr_nodes:
                (usrId, usr_type) = usr_neighbor
                current_temporal_review = G.getReview(usrId, bnssId)
                allReviews = [superGraph.getReview(usrId, super_graph_bnssId) \
                              for (super_graph_bnssId, super_graph_bnss_type) in superGraph.neighbors(usr_neighbor)]
                firstReview = min(allReviews, key= lambda x: SIAUtil.getDateForReview(x))
                    
                if firstReview.getId() == current_temporal_review.getId():
                    noOfFirstTimers+=1
            
            bnss_statistics[bnssId][StatConstants.RATIO_OF_FIRST_TIMERS][timeKey] = float(noOfFirstTimers)/float(len(reviews_for_bnss))
            
            #Youth Score
            if StatConstants.YOUTH_SCORE not in bnss_statistics[bnssId]: 
                bnss_statistics[bnssId][StatConstants.YOUTH_SCORE] = numpy.zeros(total_time_slots)
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
                
            bnss_statistics[bnssId][StatConstants.YOUTH_SCORE][timeKey] = numpy.mean(numpy.array(youth_scores))
            
            #Entropy Score
            entropyScore= 0
            
            if StatConstants.ENTROPY_SCORE not in bnss_statistics[bnssId]:
                bnss_statistics[bnssId][StatConstants.ENTROPY_SCORE] = numpy.zeros(total_time_slots)
                
            if noOfReviews >= 2:
                bucketTree = constructIntervalTree(GraphUtil.getDayIncrements(timeLength))
                allReviewsInThisTimeBlock = [G.getReview(usrId, bnssId) for (usrId, usr_type) in neighboring_usr_nodes]
                allReviewsInThisTimeBlock = sorted(allReviewsInThisTimeBlock, key = lambda x: SIAUtil.getDateForReview(x))
                allReviewVelocity = [ (SIAUtil.getDateForReview(allReviewsInThisTimeBlock[x+1]) - \
                                       SIAUtil.getDateForReview(allReviewsInThisTimeBlock[x])).days \
                                     for x in range(len(allReviewsInThisTimeBlock)-1)]
                for reviewTimeDiff in allReviewVelocity:
                    updateBucketTree(bucketTree, reviewTimeDiff)
                
                if StatConstants.REVIEW_TIME_VELOCITY not in bnss_statistics[bnssId]:
                    bnss_statistics[bnssId][StatConstants.REVIEW_TIME_VELOCITY] = dict()
                    
                bnss_statistics[bnssId][StatConstants.REVIEW_TIME_VELOCITY][timeKey] = allReviewVelocity
                 
                rating_velocity_prob_dist = {(begin,end):(count_data/(noOfReviews-1)) for (begin, end, count_data) in bucketTree}
                
                entropyScore = entropyFn(rating_velocity_prob_dist)
                
                bnss_statistics[bnssId][StatConstants.ENTROPY_SCORE][timeKey] = entropyScore
            
            
            #Max Text Similarity
            if StatConstants.MAX_TEXT_SIMILARITY not in bnss_statistics[bnssId]: 
                bnss_statistics[bnssId][StatConstants.MAX_TEXT_SIMILARITY] = numpy.zeros(total_time_slots)
                
            reviewTextsInThisTimeBlock = [G.getReview(usrId,bnssId).getReviewText()\
                                           for (usrId, usr_type) in neighboring_usr_nodes]
            
            maxTextSimilarity = 1
            if len(reviewTextsInThisTimeBlock) > 1:
                data_matrix = ShingleUtil.formDataMatrix(reviewTextsInThisTimeBlock)
                candidateGroups = ShingleUtil.jac_doc_hash(data_matrix, 20, 50)
                if len(set(candidateGroups)) == noOfReviews:
                    maxTextSimilarity = 1
                else:
                    bin_count = numpy.bincount(candidateGroups)
                    printSimilarReviews(bin_count, candidateGroups, timeKey,\
                                         bnssId, reviewTextsInThisTimeBlock) 
                    maxTextSimilarity = numpy.amax(bin_count)
                                    
            bnss_statistics[bnssId][StatConstants.MAX_TEXT_SIMILARITY][timeKey] = maxTextSimilarity
            
            if timeKey in bnss_statistics[bnssId][StatConstants.RATING_DISTRIBUTION]:
                entropy = entropyFn(bnss_statistics[bnssId][StatConstants.RATING_DISTRIBUTION][timeKey])
                bnss_statistics[bnssId][StatConstants.RATING_ENTROPY][timeKey] = entropy
                
    
    #POST PROCESSING FOR REVIEW AVERAGE_RATING and NO_OF_REVIEWS
    for bnss_key in bnss_statistics:
        statistics_for_bnss = bnss_statistics[bnss_key]
        no_of_reviews_for_bnss = statistics_for_bnss[StatConstants.NO_OF_REVIEWS]
        firstTimeKey = statistics_for_bnss[StatConstants.FIRST_TIME_KEY]
        #print statistics_for_bnss
        for timeKey in range(total_time_slots):
            if timeKey > firstTimeKey:
                fixZeroReviewTimeStamps(timeKey, statistics_for_bnss)
                        
                #POST PROCESSING FOR NUMBER_OF_REVIEWS
                statistics_for_bnss[StatConstants.NO_OF_REVIEWS][timeKey] =\
                 no_of_reviews_for_bnss[timeKey-1]+no_of_reviews_for_bnss[timeKey]
                
                #POST PROCESSING FOR AVERAGE RATING
                if no_of_reviews_for_bnss[timeKey] > 0:
                    sum_of_ratings = (statistics_for_bnss[StatConstants.AVERAGE_RATING][timeKey-1]*no_of_reviews_for_bnss[timeKey-1])
                    sum_of_ratings += statistics_for_bnss[StatConstants.AVERAGE_RATING][timeKey]
                    statistics_for_bnss[StatConstants.AVERAGE_RATING][timeKey] = sum_of_ratings/no_of_reviews_for_bnss[timeKey]
                else:
                    statistics_for_bnss[StatConstants.AVERAGE_RATING][timeKey] = 0
                
            else:
                if no_of_reviews_for_bnss[timeKey] > 0:
                    statistics_for_bnss[StatConstants.AVERAGE_RATING][timeKey] /=  statistics_for_bnss[StatConstants.NO_OF_REVIEWS][timeKey]
            
    return bnss_statistics
        

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python temporal_statistics.py fileName'
        sys.exit()
    inputFileName = sys.argv[1]
    
    beforeDataReadTime = datetime.now()
    
    rdr = ScrappedDataReader()
    (usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict) = rdr.readData(inputFileName)
    
    afterDataReadTime = datetime.now()
    
    print 'TimeTaken for Reading data:',afterDataReadTime-beforeDataReadTime
    
    beforeGraphConstructionTime = datetime.now()
    superGraph = SuperGraph.createGraph(usrIdToUserDict,\
                                             bnssIdToBusinessDict,\
                                             reviewIdToReviewsDict)
    
    cross_time_graphs = TemporalGraph.createTemporalGraph(usrIdToUserDict,\
                                             bnssIdToBusinessDict,\
                                             reviewIdToReviewsDict,\
                                             timeLength, False)
    bnssKeys = [bnss_key for bnss_key,bnss_type in superGraph.nodes()\
                 if bnss_type == SIAUtil.PRODUCT] 
                 #and \
                 #'Tommy DiNic' in bnssIdToBusinessDict[bnss_key].getName()]
    
    bnssKeys = sorted(bnssKeys, reverse=True, key = lambda x: len(superGraph.neighbors((x,SIAUtil.PRODUCT))))
    
    bnssKeySet = set(bnssKeys[:1])
    
    
    
    afterGraphConstructionTime = datetime.now()
    print 'TimeTaken for Graph Construction:',afterGraphConstructionTime-beforeGraphConstructionTime
    
    beforeStat = datetime.now()
    bnss_statistics = generateStatistics(superGraph, cross_time_graphs,\
                                          usrIdToUserDict, bnssIdToBusinessDict,\
                                           reviewIdToReviewsDict, bnssKeySet)
    afterStat = datetime.now()
    
    print 'TimeTaken for Statistics:',afterStat-beforeStat
    
    
    colors = ['g', 'c', 'r', 'b', 'm', 'y', 'k']
    
    inputDir =  join(join(join(inputFileName, os.pardir),os.pardir), 'latest')
    beforePlot = datetime.now()
    for bnssKey in bnssKeySet:
        PlotUtil.plotBnssStatistics(bnss_statistics, bnssIdToBusinessDict,\
                                     bnssKey, len(cross_time_graphs.keys()),\
                                      inputDir, random.choice(colors))
    afterPlot = datetime.now()
    print 'Time taken for Plot:',afterPlot-beforePlot