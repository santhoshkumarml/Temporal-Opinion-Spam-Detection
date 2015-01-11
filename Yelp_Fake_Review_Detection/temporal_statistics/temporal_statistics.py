'''
Created on Dec 29, 2014

@author: santhosh
'''
from datetime import datetime,timedelta
import math
import os
import networkx
import numpy
import random
import re
import sys

from util import SIAUtil
from util.ScrappedDataReader import ScrappedDataReader
from util import PlotUtil
from util import StatConstants
from os.path import join


class SuperGraph(networkx.Graph):
    def __init__(self, parentUserIdToUserDict=dict(),parentBusinessIdToBusinessDict=dict(), parent_reviews= dict()):
        super(SuperGraph, self).__init__()
        self.userIdToUserDict = parentUserIdToUserDict
        self.businessIdToBusinessDict = parentBusinessIdToBusinessDict
        self.reviewIdToReviewDict = parent_reviews
    
    
    def addNodesAndEdge(self, usr, bnss, review):
        self.userIdToUserDict[usr.getId()] = usr
        self.businessIdToBusinessDict[bnss.getId()] = bnss
        self.reviewIdToReviewDict[review.getId()] = review
        super(SuperGraph, self).add_node((usr.getId(),SIAUtil.USER))
        super(SuperGraph, self).add_node((bnss.getId(),SIAUtil.PRODUCT))
        super(SuperGraph, self).add_edge((usr.getId(),SIAUtil.USER),\
                                              (bnss.getId(),SIAUtil.PRODUCT),\
                                               attr_dict={SIAUtil.REVIEW_EDGE_DICT_CONST: review.getId()})
    
    def getUser(self, userId):
        return self.userIdToUserDict[userId]
    
    def getBusiness(self, businessId):
        return self.businessIdToBusinessDict[businessId]
        
    def getReview(self,usrId, bnssId):
        return self.reviewIdToReviewDict[self.get_edge_data((usrId,SIAUtil.USER), (bnssId,SIAUtil.PRODUCT))[SIAUtil.REVIEW_EDGE_DICT_CONST]]
    
    @staticmethod
    def createGraph(userIdToUserDict,bnssIdToBusinessDict, parent_reviews):
        graph = SuperGraph()
        for reviewKey in parent_reviews.iterkeys():
            review = parent_reviews[reviewKey]
            graph.addNodesAndEdge(usrIdToUserDict[review.getUserId()],\
                                         bnssIdToBusinessDict[review.getBusinessID()],\
                                         review)
        return graph

class TemporalGraph(networkx.Graph):
    
    def __init__(self, parentUserIdToUserDict=dict(),parentBusinessIdToBusinessDict=dict(), parent_reviews= dict()):
        super(TemporalGraph, self).__init__()
        self.userIdToUserDict = parentUserIdToUserDict
        self.businessIdToBusinessDict = parentBusinessIdToBusinessDict
        self.reviewIdToReviewDict = parent_reviews
    
    def addNodesAndEdge(self, usr, bnss, review):
        self.userIdToUserDict[usr.getId()] = usr
        self.businessIdToBusinessDict[bnss.getId()] = bnss
        self.reviewIdToReviewDict[review.getId()] = review
        super(TemporalGraph, self).add_node((usr.getId(),SIAUtil.USER))
        super(TemporalGraph, self).add_node((bnss.getId(),SIAUtil.PRODUCT))
        super(TemporalGraph, self).add_edge((usr.getId(),SIAUtil.USER),\
                                              (bnss.getId(),SIAUtil.PRODUCT),\
                                               attr_dict={SIAUtil.REVIEW_EDGE_DICT_CONST: review.getId()})
            
    def getUserCount(self):
        return len(set([node_id for (node_id, node_type) in self.nodes() if node_type == SIAUtil.USER]))
    
    def getUserIds(self):
        return [node_id for (node_id, node_type) in self.nodes() if node_type == SIAUtil.USER]
    
    def getBusinessIds(self):
        return [node_id for (node_id, node_type) in self.nodes() if node_type == SIAUtil.PRODUCT]
    
    def getBusinessCount(self):
        return len(set([node_id for (node_id, node_type) in self.nodes() if node_type == SIAUtil.PRODUCT]))
    
    def getReviewIds(self):
        return [self.get_edge_data(*edge)[SIAUtil.REVIEW_EDGE_DICT_CONST] for edge in self.edges()]
    
    def getReviewCount(self):
        return len(set([self.get_edge_data(*edge)[SIAUtil.REVIEW_EDGE_DICT_CONST] for edge in self.edges()]))
        
    def getUser(self, userId):
        return self.userIdToUserDict[userId]
    
    def getBusiness(self, businessId):
        return self.businessIdToBusinessDict[businessId]
        
    def getReview(self,usrId, bnssId):
        return self.reviewIdToReviewDict[self.get_edge_data((usrId,SIAUtil.USER), (bnssId,SIAUtil.PRODUCT))[SIAUtil.REVIEW_EDGE_DICT_CONST]]

    @staticmethod
    def createTemporalGraph(parentUserIdToUserDict,parentBusinessIdToBusinessDict, parent_reviews,\
                          timeSplit ='1-D', initializePriors=True):
        if not re.match('[0-9]+-[DMY]', timeSplit):
            print 'Time Increment does not follow the correct Pattern - Time Increment Set to 1 Day'
            timeSplit ='1-D'

        numeric = int(timeSplit.split('-')[0])
        incrementStr = timeSplit.split('-')[1]
        dayIncrement = 1
        if incrementStr=='D':
            dayIncrement = numeric
        elif incrementStr=='M':
            dayIncrement = numeric*30
        else:
            dayIncrement = numeric*365
        
        all_reviews = [SIAUtil.getDateForReview(r)\
                 for r in parent_reviews.values() ]
        minDate =  min(all_reviews)
        maxDate =  max(all_reviews)

        cross_time_graphs = dict()
        time_key = 0
    
        while time_key < ((maxDate-minDate+timedelta(dayIncrement))/dayIncrement).days:
            cross_time_graphs[time_key] = TemporalGraph()
            time_key+=1
        
        for reviewKey in parent_reviews.iterkeys():
            review = parent_reviews[reviewKey]
            reviewDate = SIAUtil.getDateForReview(review)
            timeDeltaKey = ((reviewDate-minDate)/dayIncrement).days
            temporalGraph = cross_time_graphs[timeDeltaKey]
            temporalGraph.addNodesAndEdge(usrIdToUserDict[review.getUserId()],\
                                         bnssIdToBusinessDict[review.getBusinessID()],\
                                         review)
        return cross_time_graphs

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
                bnss_statistics[bnssId][StatConstants.FIRST_TIME_KEY] = timeKey
            bnss_name = bnssIdToBusinessDict[bnssId].getName()
            #Average Rating
            if StatConstants.AVERAGE_RATING not in bnss_statistics[bnssId]:
                bnss_statistics[bnssId][StatConstants.AVERAGE_RATING] = numpy.zeros(total_time_slots)
                
            neighboring_usr_nodes = G.neighbors((bnssId,SIAUtil.PRODUCT))
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
            
            #Max Text Similarity
    
    
    #POST PROCESSING FOR REVIEW AVERAGE_RATING, NO_OF_REVIEWS, RATING_ENTROPY and ENTROPY_SCORE
    for bnss_key in bnss_statistics:
        statistics_for_bnss = bnss_statistics[bnss_key]
        no_of_reviews_for_bnss = statistics_for_bnss[StatConstants.NO_OF_REVIEWS]
        
        statistics_for_bnss[StatConstants.ENTROPY_SCORE] = numpy.zeros(total_time_slots)
        entropy_score = statistics_for_bnss[StatConstants.ENTROPY_SCORE]

        bnss_node = (bnss_key,SIAUtil.PRODUCT)
        allReviews = [superGraph.getReview(usr_neighbor[0], bnss_key)\
                       for usr_neighbor in superGraph.neighbors(bnss_node)]
        allReviews = sorted(allReviews, key = lambda x: SIAUtil.getDateForReview(x))
        allReviewVelocity = [ (SIAUtil.getDateForReview(allReviews[x+1])-SIAUtil.getDateForReview(allReviews[x])).days \
                             for x in range(len(allReviews)-1)]
        
        for reviewVelocity in allReviewVelocity:
            entropy_score[reviewVelocity]+=1
            
        
            
#         for timeKey in range(total_time_slots):
#             rating_sum_for_bnss[timeKey] = no_of_reviews_for_bnss[timeKey]*avg_rating_for_bnss[timeKey]
#             
#         if bnssIdToBusinessDict[bnss_key].getName() == 'Arizona Humane Society':
#             print statistics_for_bnss[NO_OF_REVIEWS],statistics_for_bnss[AVERAGE_RATING]
            
        for timeKey in range(total_time_slots):
            if timeKey > 0:
                #POST PROCESSING FOR NUMBER_OF_REVIEWS
                statistics_for_bnss[StatConstants.NO_OF_REVIEWS][timeKey] = no_of_reviews_for_bnss[timeKey-1]+no_of_reviews_for_bnss[timeKey]
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
            
            #POST PROCESSING FOR RATING ENTROPY
            if timeKey in statistics_for_bnss[StatConstants.RATING_DISTRIBUTION]:
                entropy = entropyFn(statistics_for_bnss[StatConstants.RATING_DISTRIBUTION][timeKey])
                if StatConstants.RATING_ENTROPY not in statistics_for_bnss:
                    statistics_for_bnss[StatConstants.RATING_ENTROPY] = numpy.zeros(total_time_slots)
                statistics_for_bnss[StatConstants.RATING_ENTROPY][timeKey] = entropy
                
#         if bnssIdToBusinessDict[bnss_key].getName() == 'Matsuhisa':               
#         if bnssIdToBusinessDict[bnss_key].getName() == 'Arizona Humane Society':
#             print statistics_for_bnss[NO_OF_REVIEWS],statistics_for_bnss[AVERAGE_RATING]
            
    return bnss_statistics



        

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
    
    bnssKeys = [bnss_key for bnss_key in bnss_statistics]
    
    bnssKeys = sorted(bnssKeys, reverse=True, key = lambda x: len(superGraph.neighbors((x,SIAUtil.PRODUCT))))
    
    colors = ['g', 'c', 'r', 'b', 'm', 'y', 'k']
    i=0
    while i<100:
        PlotUtil.plotBnssStatistics(bnss_statistics, bnssIdToBusinessDict, bnssKeys[i], len(cross_time_graphs.keys()), join(join(inputFileName, os.pardir), 'latest'), random.choice(colors))
        i+=1