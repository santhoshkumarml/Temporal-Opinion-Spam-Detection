'''
@author: santhosh
'''
from datetime import datetime
import os, csv
import pandas

from util import SIAUtil


REVIEW_ID = 'Id'
BNSS_ID = 'property_id'
USER_ID = 'user_id'
RATING = 'rating'
LAST_MODIFIED_TIMESTAMP = 'last modified'
CREATE_TIMESTAMP = 'create stamp'
REVIEW_TEXT = 'text'

RATING_CSV = 'ProductRatings_processed.csv'
REVIEW_CSV = 'ProductReviews_processed.csv'

class AnonEcommDataReader(object):
    def __init__(self):
        self.usrIdToUsrDict = {}
        self.bnssIdToBnssDict = {}
        self.reviewIdToReviewDict = {}

    def readData(self, reviewFolder, readReviewsText=False):
        beforeDataReadTime = datetime.now()
        df1 = pandas.read_csv(os.path.join(reviewFolder, RATING_CSV),
                              escapechar='\\', skiprows=1, header=None, dtype=object)
        for tup in df1.itertuples():
            idx, review_id, bnss_id, user_id, rating,\
            creation_time_stamp, last_modified_time = tup
            review_id, bnss_id, user_id, rating, creation_time_stamp = \
                review_id, bnss_id, user_id, float(rating),\
                datetime.strptime(creation_time_stamp, '%Y-%m-%d %H:%M:%S')

            if bnss_id not in self.bnssIdToBnssDict:
                self.bnssIdToBnssDict[bnss_id] = SIAUtil.business(bnss_id, bnss_id)
            bnss = self.bnssIdToBnssDict[bnss_id]

            if user_id not in self.usrIdToUsrDict:
                self.usrIdToUsrDict[user_id] = SIAUtil.user(user_id, user_id)
            usr = self.usrIdToUsrDict[user_id]

            revw = SIAUtil.review(review_id, usr.getId(), bnss.getId(), rating, creation_time_stamp)

            if review_id in self.reviewIdToReviewDict:
                print 'Already Read Meta - ReviewId:',review_id

            self.reviewIdToReviewDict[review_id] = revw

        print 'Users:', len(self.usrIdToUsrDict.keys()), \
            'Products:', len(self.bnssIdToBnssDict.keys()), \
            'Reviews:', len(self.reviewIdToReviewDict.keys())

        if not readReviewsText:
            afterDataReadTime = datetime.now()
            print 'Data Read Time:',(afterDataReadTime - beforeDataReadTime)

            return (self.usrIdToUsrDict, self.bnssIdToBnssDict, self.reviewIdToReviewDict)

        skippedDataWithNullReviewId = 0
        skippedDataWithoutReviewId = 0
        read_review_text_cnt = 0
        review_buffer = []
        with open(os.path.join(reviewFolder, REVIEW_CSV), 'rb') as csvfile:
            reviewFileReader = csv.reader((line.replace('\0','') for line in csvfile), delimiter=',', quotechar='"')
            for row in reviewFileReader:
                if len(row) > 0:
                    review_buffer = review_buffer + row
                    try:
                        int(row[-2])
                        int(row[-1])
                        revw = review_buffer[:4]
                        review_text = ' '.join(review_buffer[4:-6])
                        review_id = revw[3]
                        review_buffer = []
                        read_review_text_cnt += 1
                        if review_id != 'NULL' and review_id in self.reviewIdToReviewDict:
                            review_text = str(review_text)
                            self.reviewIdToReviewDict[review_id].setReviewText(review_text)
                            self.reviewIdToReviewDict[review_id].setExtra({'title' : review_buffer[-6],
                                                                           'category' : review_buffer[-5],
                                                                           'last_modified_time' : review_buffer[-4],
                                                                           'creation_time_stamp' : review_buffer[-3],
                                                                           'first_to_review' : review_buffer[-2],
                                                                           'certififed_buyer' : review_buffer[-1]})
                        else:
                            if review_id != 'NULL':
                                skippedDataWithNullReviewId += 1
                            else:
                                skippedDataWithoutReviewId += 1
                    except:
                        pass
#         df2 = pandas.read_csv(os.path.join(reviewFolder, REVIEW_CSV),
#                               escapechar='\\', skiprows=1, header=None, dtype=object,
#                               error_bad_lines=False)
#         for tup in df2.itertuples():
#             if len(list(tup)) != 12:
#                 skippedData += 1
#                 continue
#             index, primary_idx, bnss_id, user_id, review_id,\
#             review_text, title, vertical, last_modified_time,\
#             creation_time_stamp, first_to_review, certififed_buyer = tup
#
#             if review_id in self.reviewIdToReviewDict:
#                 review_text = str(review_text)
#                 self.reviewIdToReviewDict[review_id].setReviewText(review_text)
#             else:
#                 skippedData += 1


        afterDataReadTime = datetime.now()

        print 'Data Read Time:', (afterDataReadTime - beforeDataReadTime)
        print 'Read Count:', read_review_text_cnt, 'Skipped Count:',\
        skippedDataWithNullReviewId, skippedDataWithoutReviewId

        print 'Users:', len(self.usrIdToUsrDict.keys()), \
            'Products:', len(self.bnssIdToBnssDict.keys()), \
            'Reviews:', len(self.reviewIdToReviewDict.keys())
        textLessReviewId = set([review_id for review_id in self.reviewIdToReviewDict \
                                if not self.reviewIdToReviewDict[review_id].getReviewText() or\
                                 self.reviewIdToReviewDict[review_id].getReviewText() == ''])
        print 'No Text Reviews:', len(textLessReviewId)
#         for review_id in textLessReviewId:
#             del self.reviewIdToReviewDict[review_id]
#         print 'Removing text less reviews'
#
#         print 'Users:', len(self.usrIdToUsrDict.keys()), \
#             'Products:', len(self.bnssIdToBnssDict.keys()), \
#             'Reviews:', len(self.reviewIdToReviewDict.keys())

        return (self.usrIdToUsrDict, self.bnssIdToBnssDict, self.reviewIdToReviewDict)
