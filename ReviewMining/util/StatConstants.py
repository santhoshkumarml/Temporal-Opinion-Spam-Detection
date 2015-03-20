'''
Created on Jan 10, 2015

@author: Santhosh
'''

FIRST_TIME_KEY = 'First Time Key'

AVERAGE_RATING = 'Average Rating'
RATING_ENTROPY = 'Rating entropy'
NO_OF_REVIEWS = 'Number of Reviews'
RATIO_OF_SINGLETONS = 'Ratio of Singletons'
RATIO_OF_FIRST_TIMERS = 'Ratio of First-timers'
YOUTH_SCORE = 'Youth Score'
REVIEW_TIME_VELOCITY = 'Review Velocity'
ENTROPY_SCORE = 'Entropy Score'
RATING_DISTRIBUTION = 'Rating Distribution'
MAX_TEXT_SIMILARITY = 'Max Text Similarity'
MEASURES = [AVERAGE_RATING, RATING_ENTROPY, NO_OF_REVIEWS, RATIO_OF_SINGLETONS, RATIO_OF_FIRST_TIMERS, YOUTH_SCORE,\
            ENTROPY_SCORE, MAX_TEXT_SIMILARITY]

# r  Coefficient of forgetting type AR model. 0 <r <1  -> Decay factor or low effect from old data
# order Degree of forgetting type AR model  -> Ar model Degree
# smooth  section length of time to be moving average smoothing the calculated outliers score  - T for moving average

MEASURES_CHANGE_FINDER_PARAMS = {AVERAGE_RATING : 0.25, RATING_ENTROPY:(0.2, 1, 3),\
                           NO_OF_REVIEWS:(0.2, 1, 3), RATIO_OF_SINGLETONS:(0.5,1,3),\
                           RATIO_OF_FIRST_TIMERS:(0.5,1,3), YOUTH_SCORE:(0.5,1,3),\
                           ENTROPY_SCORE:(0.5,1,3), MAX_TEXT_SIMILARITY:(0.5,1,3)}

CUSUM = 'CUSUM'
AR_UNIFYING = 'Auto Regressive Based'

MEASURES_CHANGE_DETECTION_ALGO = {AVERAGE_RATING : CUSUM, RATING_ENTROPY:AR_UNIFYING,\
                           NO_OF_REVIEWS:AR_UNIFYING, RATIO_OF_SINGLETONS:AR_UNIFYING,\
                           RATIO_OF_FIRST_TIMERS:AR_UNIFYING, YOUTH_SCORE:AR_UNIFYING,\
                           ENTROPY_SCORE:AR_UNIFYING, MAX_TEXT_SIMILARITY:AR_UNIFYING}

MEASURES_CHANGE_FINDERS = {key:(MEASURES_CHANGE_DETECTION_ALGO[key],MEASURES_CHANGE_FINDER_PARAMS[key]) for key in MEASURES}
