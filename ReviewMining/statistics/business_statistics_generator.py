__author__ = 'santhosh'

from util import StatConstants
from datetime import datetime
import numpy
import os
from util import StatUtil
from util import SIAUtil


def extractMeasuresAndDetectAnomaliesForBnss(usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict,\
                     superGraph, cross_time_graphs, plotDir, bnssKey, timeLength,\
                     measuresToBeExtracted = StatConstants.MEASURES, logStats = False):
    beforeStat = datetime.now()
    print 'Statistics for Bnss', bnssKey
    statistics_for_current_bnss = dict()
    statistics_for_current_bnss[StatConstants.BNSS_ID] = bnssKey
    bnssStatFile = None
    if logStats:
        bnssStatFile = open(os.path.join(plotDir,bnssKey+'.stats'),'w')

    total_time_slots = len(cross_time_graphs.keys())
    firstTimeKey = None
    for timeKey in cross_time_graphs:
        G = cross_time_graphs[timeKey]
        if not firstTimeKey:
            firstTimeKey = timeKey
            statistics_for_current_bnss[StatConstants.BNSS_ID] = firstTimeKey
            statistics_for_current_bnss[StatConstants.FIRST_DATE_TIME] = G.getDateTime()
            if logStats:
                bnssStatFile.write('Business Reviews Started at:'+str(timeKey)+' '+str(G.getDateTime()))

        if bnssKey in G.getBusinessIds():
            neighboring_usr_nodes = G.neighbors((bnssKey, SIAUtil.PRODUCT))
            reviews_for_bnss = [G.getReview(usrId, bnssKey) for (usrId, usr_type) in neighboring_usr_nodes]
            ratings = [review.getRating() for review in reviews_for_bnss]

            if logStats:
                bnssStatFile.write('Reviews in Time Period:'+str(timeKey)+' '+str(G.getDateTime()))
                bnssStatFile.write('\n')
                bnssStatFile.write('Number of reviews:', len(neighboring_usr_nodes))
                bnssStatFile.write('\n')
                for review in reviews_for_bnss:
                    bnssStatFile.write(review.toString())
                    bnssStatFile.write('\n')


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

            StatUtil.doPostProcessingForStatistics(statistics_for_current_bnss, total_time_slots, measuresToBeExtracted)

    afterStat = datetime.now()
    if logStats:
        bnssStatFile.close()
