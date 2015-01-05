'''
Created on Jan 4, 2015

@author: Santhosh
'''
from util.SIAUtil import business, user, review
from os import listdir
from os.path import isfile, join
import re

NOT_RECOMMENDED = 'nonReccomended'
RECOMMENDED = 'Reccomended'
ADDRESS = 'Address'
RATING = 'Rating'
REVIEW_COUNT = 'reviewCount'
FRIEND_COUNT = 'friendCount'
NAME = 'Name'
FRIEND_COUNT = 'friendCount'
USR_LOCATION = 'Place'
REVIEW_TEXT = 'ReviewComment'
REVIEW_DATE = 'Date'

class RaviDataReader:
    def __init__(self):
        self.usrIdToUsrDict = {}
        self.bnssIdToBnssDict = {}
        self.reviewIdToReviewDict = {}
        
    def readData(self, inputDirName):
        onlyfiles = [ f for f in listdir(inputDirName) if isfile(join(inputDirName,f)) ]
        reviewIDIncrementer = 0
        for fileName in onlyfiles:
            content = 'data='
            with open(join(inputDirName, fileName), mode='r') as f:
                data = dict()
                content = content+f.readline()
                exec(content)
                bnssName = fileName.strip('.txt')
                bnssAddress = data[ADDRESS]
                bnss = business((bnssName, bnssAddress), bnssAddress)
                nrReviews = data[NOT_RECOMMENDED]
                rReviews = data[RECOMMENDED]
                
                for r in rReviews:
                    reviewIDIncrementer += 1
                    review_rating = r[RATING]
                    review_id = reviewIDIncrementer
                    review_text = r[REVIEW_TEXT]
                    review_date = r[REVIEW_DATE].split('Updated review')[0]
                    
                    usr_location = r[USR_LOCATION]
                    usr_name = r[NAME]
                    usr_review_count = r[REVIEW_COUNT]
                    usr_friend_count = r[FRIEND_COUNT]
                    usr = user((usr_name,usr_location, usr_review_count, usr_friend_count), usr_name)
                    
                    revw = review(review_id, usr.getId(), bnss.getId(), review_rating, review_date, review_text, True)
                    self.usrIdToUsrDict[usr.getId()] = usr
                    self.reviewIdToReviewDict[revw.getId()] = revw

                    
                for nr in nrReviews:
                    reviewIDIncrementer += 1
                    review_rating = nr[RATING]
                    review_id = reviewIDIncrementer
                    review_text = nr[REVIEW_TEXT]
                    review_date = nr[REVIEW_DATE].split('Updated review')[0]
                    
                    usr_location = nr[USR_LOCATION]
                    usr_name = nr[NAME]
                    usr_review_count = nr[REVIEW_COUNT]
                    usr_friend_count = nr[FRIEND_COUNT]
                    usr = user((usr_name,usr_location, usr_review_count, usr_friend_count), usr_name)
                    
                    revw = review(review_id, usr.getId(), bnss.getId(), review_rating, review_date, review_text, False)
                    
                    self.usrIdToUsrDict[usr.getId()] = usr
                    self.reviewIdToReviewDict[revw.getId()] = revw
                
                self.bnssIdToBnssDict[bnss.getId()] = bnss

        return (self.usrIdToUsrDict, self.bnssIdToBnssDict, self.reviewIdToReviewDict)