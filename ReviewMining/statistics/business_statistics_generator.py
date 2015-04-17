__author__ = 'santhosh'

from util import StatConstants
from datetime import datetime
import numpy
import os
from util import StatUtil
from util import SIAUtil
from anomaly_detection import AnomalyDetector
from util import PlotUtil

def extractMeasuresAndDetectAnomaliesForBnss(superGraph, cross_time_graphs, plotDir, bnssKey, timeLength,\
                     measuresToBeExtracted = StatConstants.MEASURES, logStats = False):
    print '--------------------------------------------------------------------------------------------------------------------'
    beforeStat = datetime.now()
    statistics_for_current_bnss = dict()
    statistics_for_current_bnss[StatConstants.BNSS_ID] = bnssKey
    bnssStatFile = None
    if logStats:
        bnssStatFile = open(os.path.join(plotDir,bnssKey+'.stats'),'w')
        bnssStatFile.write('--------------------------------------------------------------------------------------------------------------------\n')
        bnssStatFile.write('Statistics for Bnss:'+bnssKey+'\n')

    total_time_slots = len(cross_time_graphs.keys())
    isInitialized = False
    for timeKey in cross_time_graphs:
        G = cross_time_graphs[timeKey]
        if not isInitialized:
            statistics_for_current_bnss[StatConstants.BNSS_ID] = bnssKey
            statistics_for_current_bnss[StatConstants.FIRST_TIME_KEY] = timeKey
            statistics_for_current_bnss[StatConstants.FIRST_DATE_TIME] = G.getDateTime()
            isInitialized = True
            if logStats:
                bnssStatFile.write('Business Reviews Started at:'+str(timeKey)+' '+str(G.getDateTime())+'\n')

        if bnssKey in G.getBusinessIds():
            if logStats:
                bnssStatFile.write('--------------------------------------------------------------------------------------------------------------------\n')
            neighboring_usr_nodes = G.neighbors((bnssKey, SIAUtil.PRODUCT))
            reviews_for_bnss = [G.getReview(usrId, bnssKey) for (usrId, usr_type) in neighboring_usr_nodes]
            ratings = [review.getRating() for review in reviews_for_bnss]

            if logStats:
                bnssStatFile.write('Reviews in Time Period:'+str(timeKey)+' '+str(G.getDateTime()))
                bnssStatFile.write('\n')
                bnssStatFile.write('Number of reviews:'+str(len(neighboring_usr_nodes)))
                bnssStatFile.write('\n')
                for review in reviews_for_bnss:
                    bnssStatFile.write(review.toString())
                    bnssStatFile.write('\n')

            #No of Reviews
            noOfReviews = -1
            if StatConstants.NO_OF_REVIEWS in measuresToBeExtracted:
                noOfReviews = StatUtil.calculateNoOfReviews(statistics_for_current_bnss, neighboring_usr_nodes, timeKey, total_time_slots)
                if logStats:
                    bnssStatFile.write(StatConstants.NO_OF_REVIEWS+':'+\
                                       str(noOfReviews))
                    bnssStatFile.write('\n')

            #Average Rating
            if StatConstants.AVERAGE_RATING in measuresToBeExtracted:
                StatUtil.calculateAvgRating(statistics_for_current_bnss, ratings, timeKey, total_time_slots)
                if logStats:
                    bnssStatFile.write(StatConstants.AVERAGE_RATING+':'+\
                                       str(statistics_for_current_bnss[StatConstants.AVERAGE_RATING][timeKey]/noOfReviews))
                    bnssStatFile.write('\n')


            #Rating Entropy
            if StatConstants.RATING_ENTROPY in measuresToBeExtracted:
                StatUtil.calculateRatingEntropy(statistics_for_current_bnss, ratings, reviews_for_bnss, timeKey, total_time_slots)
                if logStats:
                    bnssStatFile.write(StatConstants.RATING_ENTROPY+':'+\
                                       str(statistics_for_current_bnss[StatConstants.RATING_ENTROPY][timeKey]))
                    bnssStatFile.write('\n')

            #Ratio of Singletons
            if StatConstants.RATIO_OF_SINGLETONS in measuresToBeExtracted:
                StatUtil.calculateRatioOfSingletons(statistics_for_current_bnss, neighboring_usr_nodes, reviews_for_bnss, superGraph,\
                                           timeKey, total_time_slots)
                if logStats:
                    bnssStatFile.write(StatConstants.RATIO_OF_SINGLETONS+':'+\
                                       str(statistics_for_current_bnss[StatConstants.RATIO_OF_SINGLETONS][timeKey]))
                    bnssStatFile.write('\n')

            #Ratio of First Timers
            if StatConstants.RATIO_OF_FIRST_TIMERS in measuresToBeExtracted:
                StatUtil.calculateRatioOfFirstTimers(G, statistics_for_current_bnss, neighboring_usr_nodes, reviews_for_bnss, superGraph,\
                                            timeKey, total_time_slots)
                if logStats:
                    bnssStatFile.write(StatConstants.RATIO_OF_FIRST_TIMERS+':'+\
                                       str(statistics_for_current_bnss[StatConstants.RATIO_OF_FIRST_TIMERS][timeKey]))
                    bnssStatFile.write('\n')

            #Youth Score
            if StatConstants.YOUTH_SCORE in measuresToBeExtracted:
                StatUtil.calculateYouthScore(G, statistics_for_current_bnss, neighboring_usr_nodes, superGraph, timeKey,
                                    total_time_slots)
                if logStats:
                    bnssStatFile.write(StatConstants.YOUTH_SCORE+':'+\
                                       str(statistics_for_current_bnss[StatConstants.YOUTH_SCORE][timeKey]))
                    bnssStatFile.write('\n')

            #Entropy Score
            if StatConstants.ENTROPY_SCORE in measuresToBeExtracted:
                StatUtil.calculateTemporalEntropyScore(G, statistics_for_current_bnss, neighboring_usr_nodes, noOfReviews, timeKey,
                                              timeLength, total_time_slots)
                if logStats:
                    bnssStatFile.write(StatConstants.ENTROPY_SCORE+':'+\
                                       str(statistics_for_current_bnss[StatConstants.ENTROPY_SCORE][timeKey]))
                    bnssStatFile.write('\n')

            # Max Text Similarity
            if StatConstants.MAX_TEXT_SIMILARITY in measuresToBeExtracted:
                StatUtil.calculateMaxTextSimilarity(G, statistics_for_current_bnss, neighboring_usr_nodes, noOfReviews, timeKey,
                                              timeLength, total_time_slots)
                if logStats:
                    bnssStatFile.write(StatConstants.MAX_TEXT_SIMILARITY+':'+\
                                       str(statistics_for_current_bnss[StatConstants.MAX_TEXT_SIMILARITY][timeKey]))
                    bnssStatFile.write('\n')
            bnssStatFile.write('--------------------------------------------------------------------------------------------------------------------\n')

    StatUtil.doPostProcessingForStatistics(statistics_for_current_bnss, total_time_slots, measuresToBeExtracted)
    # if logStats:
    #         for measure_key in measuresToBeExtracted:
    #             bnssStatFile.write(measure_key+':'+\
    #                                     str(statistics_for_current_bnss[StatConstants.measure_key]))
    #             bnssStatFile.write('\n')
    bnssStatFile.write('--------------------------------------------------------------------------------------------------------------------\n')

    afterStat = datetime.now()

    print 'Stats Generation Time for bnss:', bnssKey, 'in', afterStat-beforeStat

    beforeAnomalyDetection = datetime.now()

    chPtsOutliers = AnomalyDetector.detectChPtsAndOutliers(statistics_for_current_bnss, timeLength)

    afterAnomalyDetection = datetime.now()

    if logStats:
        bnssStatFile.close()
    print 'Anomaly Detection Time for bnss:', bnssKey, 'in', afterStat-beforeStat

    beforePlotTime = datetime.now()

    PlotUtil.plotMeasuresForBnss(statistics_for_current_bnss, chPtsOutliers, plotDir, measuresToBeExtracted, timeLength)

    afterPlotTime = datetime.now()

    print 'Plot Generation Time for bnss:', bnssKey, 'in', afterStat-beforeStat
    print AnomalyDetector.calculateRankingUsingAnomalies(statistics_for_current_bnss, chPtsOutliers)
    print '------------------------------------------------------------------------------------------------------------------------------'