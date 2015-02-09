'''
Created on Feb 6, 2015

@author: santhosh
'''
import sys
from os.path import join

#appid,review id,userid,username,stars,version,date,number of helpful votes,total votes,unix timestamp
META_APPID_IDX = 0
META_REVIEW_ID_IDX = 1
META_USER_ID_IDX = 2
META_STARS_IDX = 3
META_HELPFUL_VOTES_IDX = 4
META_TOTAL_VOTES_IDX = 5
META_TIMESTAMP_IDX = 6

#appid,review id,title,content
APP_ID_IDX = 0
REVIEW_ID_IDX = 1
TITLE_IDX = 2
CONTENT_IDX = 3

META_FILE = 'itunes3_reviews_meta.csv'
REVIEW_FILE = 'itunes3_reviews_text.csv'


class ItunesDataReader:
    def __init__(self):
        self.usrIdToUsrDict = {}
        self.bnssIdToBnssDict = {}
        self.reviewIdToReviewDict = {}
        
    def readData(self, reviewFolder):
        reviewMetaFile = join(reviewFolder, META_FILE)
        reviewFile = join(reviewFolder, REVIEW_FILE)
        
        with open(reviewMetaFile, 'rb') as csvfileHandle:
            metaCsvFileContent = csvfileHandle.readlines()
            print metaCsvFileContent
            