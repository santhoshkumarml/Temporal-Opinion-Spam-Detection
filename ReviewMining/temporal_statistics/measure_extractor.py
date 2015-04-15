'''
Created on Dec 29, 2014

@author: santhosh
'''
from datetime import datetime
from util import StatUtil
from util import SIAUtil
from util import StatConstants


def generateStatistics(superGraph, cross_time_graphs,\
                        usrIdToUserDict, bnssIdToBusinessDict,\
                         reviewIdToReviewsDict, bnssKeys, timeLength, measuresToBeExtracted):
    bnss_statistics = dict()
    total_time_slots = len(cross_time_graphs.keys())
    
    for timeKey in cross_time_graphs.iterkeys():
        #print timeKey
        G = cross_time_graphs[timeKey]
        for bnssId in G.getBusinessIds():
            if bnssId not in bnssKeys:
                continue
            
            if bnssId not in bnss_statistics:
                bnss_statistics[bnssId] = dict()
                bnss_statistics[bnssId][StatConstants.FIRST_TIME_KEY] = timeKey
            statistics_for_current_bnss = bnss_statistics[bnssId]
                    
            bnss_name = bnssIdToBusinessDict[bnssId].getName()
            
            neighboring_usr_nodes = G.neighbors((bnssId,SIAUtil.PRODUCT))

            reviews_for_bnss = [G.getReview(usrId,bnssId) for (usrId, usr_type) in neighboring_usr_nodes]
            ratings = [review.getRating() for review in reviews_for_bnss]

            #Average Rating
            if StatConstants.AVERAGE_RATING in measuresToBeExtracted:
                StatUtil.calculateAvgRating(statistics_for_current_bnss, ratings, timeKey, total_time_slots)
            
            #Rating Entropy
            if StatConstants.RATING_ENTROPY in measuresToBeExtracted:
                StatUtil.calculateRatingEntropy(statistics_for_current_bnss, ratings, reviews_for_bnss, timeKey, total_time_slots)

            #No of Reviews
            # if StatConstants.NO_OF_REVIEWS in measuresToBeExtracted:
            noOfReviews = StatUtil.calculateNoOfReviews(statistics_for_current_bnss, neighboring_usr_nodes, timeKey, total_time_slots)
            
            #Ratio of Singletons
            if StatConstants.RATIO_OF_SINGLETONS in measuresToBeExtracted:
                StatUtil.calculateRatioOfSingletons(statistics_for_current_bnss, neighboring_usr_nodes, reviews_for_bnss, superGraph,\
                                           timeKey, total_time_slots)
            
            #Ratio of First Timers
            if StatConstants.RATIO_OF_FIRST_TIMERS in measuresToBeExtracted:
                StatUtil.calculateRatioOfFirstTimers(G, statistics_for_current_bnss, neighboring_usr_nodes, reviews_for_bnss, superGraph,\
                                            timeKey, total_time_slots)
            
            #Youth Score
            if StatConstants.YOUTH_SCORE in measuresToBeExtracted:
                StatUtil.calculateYouthScore(G, statistics_for_current_bnss, neighboring_usr_nodes, superGraph, timeKey,
                                    total_time_slots)
            
            #Entropy Score
            if StatConstants.ENTROPY_SCORE in measuresToBeExtracted:
                StatUtil.calculateTemporalEntropyScore(G, statistics_for_current_bnss, neighboring_usr_nodes, noOfReviews, timeKey,
                                              timeLength, total_time_slots)

            # Max Text Similarity
            if StatConstants.MAX_TEXT_SIMILARITY in measuresToBeExtracted:
                StatUtil.calculateMaxTextSimilarity(G, statistics_for_current_bnss, neighboring_usr_nodes, noOfReviews, timeKey,
                                              timeLength, total_time_slots)

    StatUtil.doPostProcessingForStatistics(statistics_for_current_bnss, total_time_slots)
            
    return bnss_statistics


def trySmoothing(bnss_statistics, measures_To_Be_Extracted):
    for bnss_key in bnss_statistics:
        for measure_key in measures_To_Be_Extracted:
            if measure_key in {StatConstants.AVERAGE_RATING, StatConstants.NO_OF_REVIEWS}:
                continue
            stat = bnss_statistics[bnss_key][measure_key]
            r,order,smooth = StatConstants.MEASURES_CHANGE_FINDERS[measure_key]
            firstKey = bnss_statistics[bnss_key][StatConstants.FIRST_TIME_KEY]
            for i in range(firstKey+1,smooth):
                stat[i] = stat[i-1]+stat[i+1]
                stat[i] /= 3

def extractMeasures(usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict,\
                     superGraph, cross_time_graphs, plotDir, bnssKeySet, timeLength,\
                     measures_To_Be_Extracted = StatConstants.MEASURES):
    
    beforeStat = datetime.now()
    bnss_statistics = generateStatistics(superGraph, cross_time_graphs,\
                                          usrIdToUserDict, bnssIdToBusinessDict,\
                                           reviewIdToReviewsDict, bnssKeySet,\
                                          timeLength, measures_To_Be_Extracted)
    afterStat = datetime.now()
    
    print 'TimeTaken for Statistics:',afterStat-beforeStat
    
    return bnss_statistics