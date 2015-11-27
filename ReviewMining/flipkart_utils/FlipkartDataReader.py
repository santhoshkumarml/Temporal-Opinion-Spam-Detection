__author__ = 'santhosh'
import sys
import pandas

REVIEW_ID = 'Id'
BNSS_ID = 'property_id'
USER_ID = 'user_id'
RATING = 'rating'
LAST_MODIFIED_TIMESTAMP = 'last modified'
CREATE_TIMESTAMP = 'create stamp'
REVIEW_TEXT = 'text'

RATING_CSV = 'ProductRatings_processed.csv'
REVIEW_CSV = 'ProductReviews_processed.csv'
RATING_CSV_COLS = [REVIEW_ID, BNSS_ID, USER_ID, RATING, CREATE_TIMESTAMP]
REVIEW_CSV_COLS = [REVIEW_ID, BNSS_ID, USER_ID, REVIEW_TEXT]

class FlipkartDataReader(object):
    def __init__(self):
        self.usrIdToUsrDict = {}
        self.bnssIdToBnssDict = {}
        self.reviewIdToReviewDict = {}

    def readData(self, reviewFolder, readReviewsText=False):
        RATING_CSV_COLS = [REVIEW_ID, BNSS_ID, USER_ID, RATING, CREATE_TIMESTAMP]
        df1 = pandas.read_csv(RATING_CSV, escapechar='\\',header=None, \
                          dtype=object, names=RATING_CSV_COLS)
        for index, review_id, bnss_id, user_id, rating, time_stamp in df1.itertuples():
            print bnss_id, review_id, rating, rating, time_stamp
            sys.exit()