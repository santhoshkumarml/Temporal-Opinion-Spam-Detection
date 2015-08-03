'''
Created on Jan 10, 2015

@author: Santhosh
'''

FIRST_TIME_KEY = 'First Time Key'
LAST_TIME_KEY = 'Last Time Key'
FIRST_DATE_TIME = 'First Date Time'
LAST_DATE_TIME = 'Last Date Time'
BNSS_ID = 'BNSS_ID'

AVERAGE_RATING = 'Average Rating'
RATING_ENTROPY = 'Rating entropy'
NO_OF_REVIEWS = 'Number of Reviews'
NON_CUM_NO_OF_REVIEWS = 'Non Cumulative Number of Reviews'
NO_OF_POSITIVE_REVIEWS = 'Number of Positive Reviews'
NO_OF_NEGATIVE_REVIEWS = 'Number of Negative Reviews'
RATIO_OF_SINGLETONS = 'Ratio of Singletons'
RATIO_OF_FIRST_TIMERS = 'Ratio of First-timers'
YOUTH_SCORE = 'Youth Score'
REVIEW_TIME_VELOCITY = 'Review Velocity'
ENTROPY_SCORE = 'Entropy Gap Score'
RATING_DISTRIBUTION = 'Rating Distribution'
MAX_TEXT_SIMILARITY = 'Max Text Similarity'
TF_IDF = 'TF_IDF'
MEASURES = [AVERAGE_RATING, RATING_ENTROPY, NON_CUM_NO_OF_REVIEWS, RATIO_OF_SINGLETONS, RATIO_OF_FIRST_TIMERS, YOUTH_SCORE,\
            ENTROPY_SCORE,NO_OF_POSITIVE_REVIEWS, NO_OF_NEGATIVE_REVIEWS, MAX_TEXT_SIMILARITY, NO_OF_REVIEWS, TF_IDF]

# r  Coefficient of forgetting type AR model. 0 <r <1  -> Decay factor or low effect from old data
# order Degree of forgetting type AR model  -> Ar model Degree
# smooth  section length of time to be moving average smoothing the calculated outliers score  - T for moving average

MEASURES_CHANGE_FINDER_PARAMS = {AVERAGE_RATING : 0.5, RATING_ENTROPY:(0.2, 1, 3),\
                           NON_CUM_NO_OF_REVIEWS:(0.2, 1, 3), NO_OF_POSITIVE_REVIEWS:(0.2, 1, 3),\
                                 NO_OF_NEGATIVE_REVIEWS:(0.2, 1, 3), RATIO_OF_SINGLETONS:(0.5,1,3),\
                           RATIO_OF_FIRST_TIMERS:(0.5,1,3), YOUTH_SCORE:(0.5,1,3),\
                           ENTROPY_SCORE:(0.5,1,3), MAX_TEXT_SIMILARITY:(0.5,1,3), TF_IDF:(0.5, 1, 3),\
                                 NO_OF_REVIEWS:(0.2, 1, 3)}

CUSUM = 'CUSUM'
LOCAL_AR = 'LOCAL_AR'
LOCAL_GRANGER = 'LOCAL_GRANGER'
AR_UNIFYING = 'SDAR'
TWITTER_SEASONAL_ANOM_DETECTION = 'Twitter Anomaly Detection in Time Series'

MEASURES_CHANGE_DETECTION_ALGO = {AVERAGE_RATING : CUSUM, RATING_ENTROPY:AR_UNIFYING,\
                           NON_CUM_NO_OF_REVIEWS: AR_UNIFYING, RATIO_OF_SINGLETONS:AR_UNIFYING,\
                           NO_OF_POSITIVE_REVIEWS: AR_UNIFYING, NO_OF_NEGATIVE_REVIEWS:AR_UNIFYING,\
                           RATIO_OF_FIRST_TIMERS:AR_UNIFYING, YOUTH_SCORE:AR_UNIFYING,\
                           ENTROPY_SCORE:AR_UNIFYING, MAX_TEXT_SIMILARITY:AR_UNIFYING,\
                                  TF_IDF:AR_UNIFYING, NO_OF_REVIEWS: AR_UNIFYING}


# MEASURES_CHANGE_DETECTION_ALGO = {AVERAGE_RATING : CUSUM, RATING_ENTROPY:LOCAL_AR,\
#                            NON_CUM_NO_OF_REVIEWS: LOCAL_AR, RATIO_OF_SINGLETONS:LOCAL_AR,\
#                            RATIO_OF_FIRST_TIMERS:LOCAL_AR, YOUTH_SCORE:LOCAL_AR,\
#                            ENTROPY_SCORE:LOCAL_AR, MAX_TEXT_SIMILARITY:LOCAL_AR,\
#                                   TF_IDF:LOCAL_AR, NO_OF_REVIEWS: LOCAL_AR}

# MEASURES_CHANGE_DETECTION_ALGO = {AVERAGE_RATING : CUSUM, RATING_ENTROPY:LOCAL_GRANGER,\
#                            NON_CUM_NO_OF_REVIEWS: LOCAL_AR, RATIO_OF_SINGLETONS:LOCAL_GRANGER,\
#                            RATIO_OF_FIRST_TIMERS:LOCAL_GRANGER, YOUTH_SCORE:LOCAL_GRANGER,\
#                            ENTROPY_SCORE:LOCAL_GRANGER, MAX_TEXT_SIMILARITY:LOCAL_GRANGER,\
#                                   TF_IDF:LOCAL_GRANGER, NO_OF_REVIEWS: LOCAL_AR}

MEASURES_CHANGE_FINDERS = {key:(MEASURES_CHANGE_DETECTION_ALGO[key],MEASURES_CHANGE_FINDER_PARAMS[key]) for key in MEASURES}


BOTH = 'both'
INCREASE = 'Increase'
DECREASE = 'Decrease'
MEASURE_DIRECTION = {AVERAGE_RATING : BOTH, RATING_ENTROPY:DECREASE,\
                           NON_CUM_NO_OF_REVIEWS:INCREASE, RATIO_OF_SINGLETONS:INCREASE,\
                           RATIO_OF_FIRST_TIMERS:INCREASE, YOUTH_SCORE:INCREASE,\
                           ENTROPY_SCORE:DECREASE, MAX_TEXT_SIMILARITY:INCREASE, TF_IDF:BOTH,\
                     NO_OF_REVIEWS: INCREASE, NO_OF_POSITIVE_REVIEWS:INCREASE, NO_OF_POSITIVE_REVIEWS:DECREASE}

MEASURE_CHANGE_THRES = {AVERAGE_RATING : 0.5, RATING_ENTROPY:0.5,\
                           NON_CUM_NO_OF_REVIEWS:250, RATIO_OF_SINGLETONS:0.4,\
                           RATIO_OF_FIRST_TIMERS:0.4, YOUTH_SCORE:0.5,\
                           ENTROPY_SCORE:0.6, MAX_TEXT_SIMILARITY:None, TF_IDF:None,\
                        NO_OF_REVIEWS:None, NO_OF_POSITIVE_REVIEWS:None, NO_OF_NEGATIVE_REVIEWS:None}

MEASURE_CHANGE_LOCAL_AR_THRES = {AVERAGE_RATING : 0.5, RATING_ENTROPY: 0.25,\
                           NON_CUM_NO_OF_REVIEWS:40000, RATIO_OF_SINGLETONS:0.16,\
                           RATIO_OF_FIRST_TIMERS: 0.16, YOUTH_SCORE: 0.25,\
                           ENTROPY_SCORE: 0.36, MAX_TEXT_SIMILARITY: None,\
                                 TF_IDF: None, NO_OF_REVIEWS: None, NO_OF_POSITIVE_REVIEWS:None,
                                 NO_OF_NEGATIVE_REVIEWS:None}

MEASURE_CHANGE_LOCAL_GRANGER_THRES = {AVERAGE_RATING : 0.5, RATING_ENTROPY: 0.25,\
                           NON_CUM_NO_OF_REVIEWS:40000, RATIO_OF_SINGLETONS:0.16,\
                           RATIO_OF_FIRST_TIMERS: 0.16, YOUTH_SCORE: 0.25,\
                           ENTROPY_SCORE: 0.36, MAX_TEXT_SIMILARITY: None,\
                                 TF_IDF: None, NO_OF_REVIEWS: None}