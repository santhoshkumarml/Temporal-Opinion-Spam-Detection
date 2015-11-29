import math

__author__ = 'santhosh'
import StatConstants
import numpy
from intervaltree import IntervalTree
from lsh import ShingleUtil
from util import SIAUtil
from util import GraphUtil
import nltk

nltk.data.path.append('/media/santhosh/Data/workspace/nltk_data')

def entropyFn(probability_dict):
    entropy = 0
    for key in probability_dict:
        probability = probability_dict[key]
        if probability > 0:
            entropy += -(probability * math.log(probability, 2))
    return entropy


def sigmoid_prime(x):
    return (2.0/(1+math.exp(-x)))-1


def constructIntervalTree(days):
    t = IntervalTree()
    end = days
    t[0:1] = 0
    iter_start = 1
    step_index = 0
    while iter_start < end:
        iterend = iter_start + (2**step_index)
        t[iter_start:iterend] = 0
        iter_start = iterend
        step_index += 1
    return t


def getBucketIntervalForBucketTree(bucketTree, point):
    bucket_intervals = list(bucketTree[point])
    assert len(bucket_intervals) == 1
    return bucket_intervals[0]

def updateBucketTree(bucketTree, point):
    interval = getBucketIntervalForBucketTree(bucketTree, point)
    begin, end, data = interval
    bucketTree.remove(interval)
    bucketTree[begin:end] = data + 1.0

def fixZeroReviewTimeStamps(timeKey, statistics_for_bnss):
    noOfReviewsInTime = statistics_for_bnss[StatConstants.NO_OF_REVIEWS][timeKey]
    for measure_key in StatConstants.MEASURES:
        if measure_key not in statistics_for_bnss or measure_key == StatConstants.NON_CUM_NO_OF_REVIEWS:
            continue
        if measure_key != StatConstants.NO_OF_REVIEWS and measure_key != StatConstants.AVERAGE_RATING and\
                        measure_key != StatConstants.MAX_TEXT_SIMILARITY:
            if noOfReviewsInTime == 0:
                statistics_for_bnss[measure_key][timeKey] = statistics_for_bnss[measure_key][timeKey - 1]

def calculateAvgRating(statistics_for_bnss, ratings, timeKey, total_time_slots):
    if StatConstants.AVERAGE_RATING not in statistics_for_bnss:
        statistics_for_bnss[StatConstants.AVERAGE_RATING] = numpy.zeros(total_time_slots)
    statistics_for_bnss[StatConstants.AVERAGE_RATING][timeKey] = float(sum(ratings))


def calculateRatingEntropy(statistics_for_bnss, ratings, reviews_for_bnss, timeKey, total_time_slots):
    sorted_rating_list = set(sorted(ratings))

    if StatConstants.RATING_DISTRIBUTION not in statistics_for_bnss:
        statistics_for_bnss[StatConstants.RATING_DISTRIBUTION] = dict()

    if StatConstants.RATING_ENTROPY not in statistics_for_bnss:
        statistics_for_bnss[StatConstants.RATING_ENTROPY] = numpy.zeros(total_time_slots)

    if timeKey not in statistics_for_bnss[StatConstants.RATING_DISTRIBUTION]:
        statistics_for_bnss[StatConstants.RATING_DISTRIBUTION][timeKey] = {key: 0.0 for key in sorted_rating_list}

    for rating in ratings:
        statistics_for_bnss[StatConstants.RATING_DISTRIBUTION][timeKey][rating] += 1.0

    for rating in sorted_rating_list:
        statistics_for_bnss[StatConstants.RATING_DISTRIBUTION][timeKey][rating] /= float(len(reviews_for_bnss))

    if timeKey in statistics_for_bnss[StatConstants.RATING_DISTRIBUTION]:
            entropy = entropyFn(statistics_for_bnss[StatConstants.RATING_DISTRIBUTION][timeKey])
            statistics_for_bnss[StatConstants.RATING_ENTROPY][timeKey] = entropy

def calculateNoOfReviews(statistics_for_bnss, neighboring_usr_nodes, timeKey, total_time_slots):
    if StatConstants.NO_OF_REVIEWS not in statistics_for_bnss:
        statistics_for_bnss[StatConstants.NO_OF_REVIEWS] = numpy.zeros(total_time_slots, dtype=int)
    noOfReviews = len(neighboring_usr_nodes)
    statistics_for_bnss[StatConstants.NO_OF_REVIEWS][timeKey] = noOfReviews
    return noOfReviews

def calculateNoOfPositiveAndNegativeReviews(G, statistics_for_bnss, neighboring_usr_nodes, timeKey, total_time_slots):
    if StatConstants.NO_OF_POSITIVE_REVIEWS not in statistics_for_bnss:
        statistics_for_bnss[StatConstants.NO_OF_POSITIVE_REVIEWS] = numpy.zeros(total_time_slots, dtype=int)

    if StatConstants.NO_OF_NEGATIVE_REVIEWS not in statistics_for_bnss:
        statistics_for_bnss[StatConstants.NO_OF_NEGATIVE_REVIEWS] = numpy.zeros(total_time_slots, dtype=int)

    noOfPReviews = 0
    noOfNReviews = 0
    for usr_neighbor in neighboring_usr_nodes:
        (usrId, usr_type) = usr_neighbor
        current_temporal_review = G.getReview(usrId, statistics_for_bnss[StatConstants.BNSS_ID])
        reviewSentiment = current_temporal_review.getReviewSentiment()

        if reviewSentiment == SIAUtil.REVIEW_TYPE_POSITIVE:
            noOfPReviews += 1
        elif reviewSentiment == SIAUtil.REVIEW_TYPE_NEGATIVE:
            noOfNReviews += 1
        else:
            pass
    statistics_for_bnss[StatConstants.NO_OF_POSITIVE_REVIEWS][timeKey] = noOfPReviews
    statistics_for_bnss[StatConstants.NO_OF_NEGATIVE_REVIEWS][timeKey] = noOfNReviews


def calculateRatioOfSingletons(statistics_for_bnss, neighboring_usr_nodes, reviews_for_bnss, superGraph, timeKey,
                               total_time_slots):
    if StatConstants.RATIO_OF_SINGLETONS not in statistics_for_bnss:
        statistics_for_bnss[StatConstants.RATIO_OF_SINGLETONS] = numpy.zeros(total_time_slots)
    noOfSingleTons = 0
    for neighbor in neighboring_usr_nodes:
        if len(superGraph.neighbors(neighbor)) == 1:
            noOfSingleTons += 1
    statistics_for_bnss[StatConstants.RATIO_OF_SINGLETONS][timeKey] = float(noOfSingleTons) / float(
        len(reviews_for_bnss))


def calculateRatioOfFirstTimers(G, statistics_for_bnss, neighboring_usr_nodes, reviews_for_bnss, superGraph,
                                timeKey, total_time_slots):
    if StatConstants.RATIO_OF_FIRST_TIMERS not in statistics_for_bnss:
        statistics_for_bnss[StatConstants.RATIO_OF_FIRST_TIMERS] = numpy.zeros(total_time_slots)
    noOfFirstTimers = 0
    for usr_neighbor in neighboring_usr_nodes:
        (usrId, usr_type) = usr_neighbor
        current_temporal_review = G.getReview(usrId, statistics_for_bnss[StatConstants.BNSS_ID])
        allReviews = [superGraph.getReview(usrId, super_graph_bnssId) \
                      for (super_graph_bnssId, super_graph_bnss_type) in superGraph.neighbors(usr_neighbor)]
        firstReview = min(allReviews, key=lambda x: SIAUtil.getDateForReview(x))

        if firstReview.getId() == current_temporal_review.getId():
            noOfFirstTimers += 1
    statistics_for_bnss[StatConstants.RATIO_OF_FIRST_TIMERS][timeKey] = float(noOfFirstTimers) / float(
        len(reviews_for_bnss))


def calculateYouthScore(G, statistics_for_bnss, neighboring_usr_nodes, superGraph, timeKey, total_time_slots):
    if StatConstants.YOUTH_SCORE not in statistics_for_bnss:
        statistics_for_bnss[StatConstants.YOUTH_SCORE] = numpy.zeros(total_time_slots)
    youth_scores = []
    for usr_neighbor in neighboring_usr_nodes:
        (usrId, usr_type) = usr_neighbor
        allReviews = [superGraph.getReview(usrId, super_graph_bnssId) \
                      for (super_graph_bnssId, super_graph_bnss_type) in superGraph.neighbors(usr_neighbor)]
        allReviews = sorted(allReviews, key=lambda x: SIAUtil.getDateForReview(x))
        current_temporal_review = G.getReview(usrId, statistics_for_bnss[StatConstants.BNSS_ID])
        reviewAge = (SIAUtil.getDateForReview(current_temporal_review) - SIAUtil.getDateForReview(allReviews[0])).days
        youth_score = 1 - sigmoid_prime(reviewAge)
        youth_scores.append(youth_score)
    statistics_for_bnss[StatConstants.YOUTH_SCORE][timeKey] = numpy.mean(numpy.array(youth_scores))

def getDateDiff(diff):
    if StatConstants.MINIMUM_GRANULARITY == StatConstants.DAY_GRANULARITY:
        return diff.days
    elif StatConstants.MINIMUM_GRANULARITY == StatConstants.HOUR_GRANULARITY:
        return diff.hour
    elif StatConstants.MINIMUM_GRANULARITY == StatConstants.MINUTE_GRANULARITY:
        return diff.minute

def calculateTemporalEntropyScore(G, statistics_for_bnss, neighboring_usr_nodes, noOfReviews,
                                  timeKey, timeLength,
                                  total_time_slots):
    entropyScore = 0
    if StatConstants.ENTROPY_SCORE not in statistics_for_bnss:
        statistics_for_bnss[StatConstants.ENTROPY_SCORE] = numpy.zeros(total_time_slots)
    if noOfReviews >= 2:
        granularity_inc = GraphUtil.getGranularityInc(GraphUtil.getDayIncrements(timeLength))
        bucketTree = constructIntervalTree(granularity_inc)
        allReviewsInThisTimeBlock = [G.getReview(usrId, statistics_for_bnss[StatConstants.BNSS_ID])
                                     for (usrId, usr_type) in neighboring_usr_nodes]
        allReviewsInThisTimeBlock = sorted(allReviewsInThisTimeBlock, key=lambda x: SIAUtil.getDateForReview(x))
        allReviewVelocity = [getDateDiff(SIAUtil.getDateForReview(allReviewsInThisTimeBlock[x + 1]) -
                              SIAUtil.getDateForReview(allReviewsInThisTimeBlock[x])).days
                             for x in range(len(allReviewsInThisTimeBlock) - 1)]
        for reviewTimeDiff in allReviewVelocity:
            updateBucketTree(bucketTree, reviewTimeDiff)

        if StatConstants.REVIEW_TIME_VELOCITY not in statistics_for_bnss:
            statistics_for_bnss[StatConstants.REVIEW_TIME_VELOCITY] = dict()

        statistics_for_bnss[StatConstants.REVIEW_TIME_VELOCITY][timeKey] = allReviewVelocity

        rating_velocity_prob_dist = {(begin, end): (count_data / (noOfReviews - 1)) for (begin, end, count_data) in
                                     bucketTree}

        entropyScore = entropyFn(rating_velocity_prob_dist)

        statistics_for_bnss[StatConstants.ENTROPY_SCORE][timeKey] = entropyScore

def calculateMaxTextSimilarity(G, statistics_for_bnss, neighboring_usr_nodes, noOfReviews, timeKey, timeLength,
                                  total_time_slots):
    if StatConstants.MAX_TEXT_SIMILARITY not in statistics_for_bnss:
        statistics_for_bnss[StatConstants.MAX_TEXT_SIMILARITY] = numpy.zeros(total_time_slots)

    reviewTextsInThisTimeBlock = [G.getReview(usrId,statistics_for_bnss[StatConstants.BNSS_ID]).getReviewText()\
                                    for (usrId, usr_type) in neighboring_usr_nodes]
    maxTextSimilarity = 1
    if len(reviewTextsInThisTimeBlock) > 1:
        data_matrix = ShingleUtil.formDataMatrix(reviewTextsInThisTimeBlock)
        candidateGroups = ShingleUtil.jac_doc_hash(data_matrix, 20, 50)
        if len(set(candidateGroups)) == noOfReviews:
            maxTextSimilarity = 1
        else:
            bin_count = numpy.bincount(candidateGroups)
            printSimilarReviews(bin_count, candidateGroups, reviewTextsInThisTimeBlock, timeKey,\
                                 statistics_for_bnss[StatConstants.BNSS_ID])
            maxTextSimilarity = numpy.amax(bin_count)

    statistics_for_bnss[StatConstants.MAX_TEXT_SIMILARITY][timeKey] = maxTextSimilarity


def printSimilarReviews(bin_count, candidateGroups, reviewTextsInThisTimeBlock, time_key, bnssKey,):
    bucketNumbers = set([i for i in range(len(bin_count)) if bin_count[i]>1])
    bucketIndexListPair = []
    for bucketNumber in bucketNumbers:
        indexes = [i for i in range(len(candidateGroups)) if candidateGroups[i]==bucketNumber]
        bucketIndexListPair.append((bucketNumber,indexes))
    print '-------------------------'
    print bnssKey, time_key
    for bucketNumber,indexes in bucketIndexListPair:
        print '-------------------------'
        print bucketNumber
        for index in indexes:
            print reviewTextsInThisTimeBlock[index]
        print '-------------------------'
    print '-------------------------'


def calculateTopTFIDF(G, statistics_for_bnss, neighboring_usr_nodes, noOfReviews, timeKey, total_time_slots):
    if StatConstants.TF_IDF not in statistics_for_bnss:
        statistics_for_bnss[StatConstants.TF_IDF] = numpy.zeros(total_time_slots)

    reviewTextsInThisTimeBlock = [G.getReview(usrId, statistics_for_bnss[StatConstants.BNSS_ID]).getReviewText()\
                                    for (usrId, usr_type) in neighboring_usr_nodes]
    # print reviewTextsInThisTimeBlock
    all_words_cnt_dict = dict()

    all_reviewTexts_in_curr_time_stamp = [G.getReviewFromReviewId(reviewId).getReviewText() for reviewId in G.getReviewIds()]
    # for usrId in G.getUserIds():
    #     for bnssId in G.getBusinessIds():
    #         review = G.getReview(usrId, bnssId).getReviewText()
    #         all_reviews_in_curr_time_stamp.append(review)

    for reviewText in all_reviewTexts_in_curr_time_stamp:
        words = nltk.word_tokenize(reviewText.decode('utf8'))
        for word in words:
            if word not in all_words_cnt_dict:
                all_words_cnt_dict[word] = 0.0
            all_words_cnt_dict[word] += 1.0

    current_bnss_cnt_dict = dict()
    for reviewText in reviewTextsInThisTimeBlock:
        words = nltk.word_tokenize(reviewText.decode('utf8'))
        for word in words:
            if word not in current_bnss_cnt_dict:
                current_bnss_cnt_dict[word] = 0.0
            current_bnss_cnt_dict[word] += 1.0

    tota_freq = sum(current_bnss_cnt_dict.values())
    tf = current_bnss_cnt_dict
    tf = {key: tf[key]/tota_freq for key in tf.keys()}

    no_of_reviews_in_time_stamp = len(all_reviewTexts_in_curr_time_stamp)
    idf = all_words_cnt_dict
    idf = {key: math.log(no_of_reviews_in_time_stamp/idf[key]) for key in idf.keys()}
    tfidf = {key:tf[key]*idf[key] for key in tf.keys()}

    top_tf_idf_word = max(tfidf.keys(), key=lambda key: tfidf[key])
    statistics_for_bnss[StatConstants.TF_IDF][timeKey] = tfidf[top_tf_idf_word]
    return top_tf_idf_word

def doPostProcessingForStatistics(statistics_for_bnss, total_time_slots, measuresToBeExtracted = StatConstants.MEASURES):
    # POST PROCESSING FOR REVIEW AVERAGE_RATING and NO_OF_REVIEWS
    no_of_reviews_for_bnss = statistics_for_bnss[StatConstants.NO_OF_REVIEWS]
    firstTimeKey = statistics_for_bnss[StatConstants.FIRST_TIME_KEY]
    lastTimeKey = statistics_for_bnss[StatConstants.LAST_TIME_KEY]
    if StatConstants.NON_CUM_NO_OF_REVIEWS in measuresToBeExtracted:
        statistics_for_bnss[StatConstants.NON_CUM_NO_OF_REVIEWS] = numpy.copy(statistics_for_bnss[StatConstants.NO_OF_REVIEWS])

    for timeKey in range(total_time_slots):
        if timeKey >= firstTimeKey and timeKey <=lastTimeKey:
            fixZeroReviewTimeStamps(timeKey, statistics_for_bnss)
            #POST PROCESSING FOR NUMBER_OF_REVIEWS
            statistics_for_bnss[StatConstants.NO_OF_REVIEWS][timeKey] = \
                no_of_reviews_for_bnss[timeKey - 1] + no_of_reviews_for_bnss[timeKey]
            #POST PROCESSING FOR AVERAGE RATING
            if no_of_reviews_for_bnss[timeKey] > 0:
                sum_of_ratings = (
                statistics_for_bnss[StatConstants.AVERAGE_RATING][timeKey - 1] * no_of_reviews_for_bnss[
                    timeKey - 1])
                sum_of_ratings += statistics_for_bnss[StatConstants.AVERAGE_RATING][timeKey]
                statistics_for_bnss[StatConstants.AVERAGE_RATING][timeKey] = sum_of_ratings / \
                                                                                no_of_reviews_for_bnss[timeKey]
            else:
                statistics_for_bnss[StatConstants.AVERAGE_RATING][timeKey] = 0

        else:
            if no_of_reviews_for_bnss[timeKey] > 0:
                statistics_for_bnss[StatConstants.AVERAGE_RATING][timeKey] /= \
                statistics_for_bnss[StatConstants.NO_OF_REVIEWS][timeKey]