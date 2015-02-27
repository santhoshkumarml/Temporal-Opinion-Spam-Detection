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
MEASURES_CHANGE_FINDERS = {AVERAGE_RATING : (0.5,1,8), RATING_ENTROPY:(0.5,1,3), NO_OF_REVIEWS:(0.5,1,8), RATIO_OF_SINGLETONS:(0.5,1,3), RATIO_OF_FIRST_TIMERS:(0.5,1,3), YOUTH_SCORE:(0.5,1,3),\
            ENTROPY_SCORE:(0.5,1,3), MAX_TEXT_SIMILARITY:(0.5,1,3)}
