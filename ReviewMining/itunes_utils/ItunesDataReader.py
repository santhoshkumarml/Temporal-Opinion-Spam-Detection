'''
Created on Feb 6, 2015

@author: santhosh
'''
import pandas as pd
import sys
from os.path import join
from util.SIAUtil import user, business, review
from datetime import datetime, date
import dateutil

#appid,review id,userid,username,stars,version,date,number of helpful votes,total votes,unix timestamp
META_BNSS_ID = 'bnss_id'
META_REVIEW_ID = 'review_id'
META_USER_ID = 'user_id'
META_USER_NAME = 'username'
META_STARS = 'stars'
META_BNSS_VERSION = 'version'
META_DATE  = 'date'
META_HELPFUL_VOTES ='Helpful Votes' 
META_TOTAL_VOTES = 'Total Votes'
META_TIMESTAMP = 'Timestamp'
META_COLS = [META_BNSS_ID,  META_REVIEW_ID, META_USER_ID, META_USER_NAME, \
             META_STARS, META_BNSS_VERSION, META_DATE, META_HELPFUL_VOTES, \
             META_TOTAL_VOTES, META_TIMESTAMP]

META_IDX_DICT = {META_COLS[i]:i for i in range(len(META_COLS))}

#appid,review id,title,content
BNSS_ID = 'bnss_id'
REVIEW_ID = 'review_id'
TITLE = 'title'
CONTENT = 'content' 
COLS = [BNSS_ID, REVIEW_ID, TITLE, CONTENT]

REVW_IDX_DICT = {COLS[i]:i for i in range(len(COLS))}

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
        with open(reviewMetaFile, 'r') as f:
            lines = f.read().splitlines()
            for line in lines:
                line = line.replace('\,','')
                row = line.split(',')
                if len(row) > len(META_COLS):
                    print 'skipping'
                    continue
                bnss_id = row[META_IDX_DICT[META_BNSS_ID]]
                user_id = row[META_IDX_DICT[META_USER_ID]]
                user_name = row[META_IDX_DICT[META_USER_NAME]]
                review_id = row[META_IDX_DICT[META_REVIEW_ID]]
                stars = row[META_IDX_DICT[META_STARS]]
                review_date = row[META_IDX_DICT[META_DATE]]
                
                length = len(review_date)
                review_date = review_date[0:length-4]+','+review_date[length-4:]
                print bnss_id, review_id, user_id, user_name, stars, review_date
                review_id = (bnss_id, review_id)
                try :
                    date_object = dateutil.parser.parse(review_date)
                    date_object = date_object.date()
                    stars = float(stars)
                except:
                    e = sys.exc_info()[0]
                    print 'skipping'
                    continue
            
                if bnss_id not in self.bnssIdToBnssDict:
                    self.bnssIdToBnssDict[bnss_id] = business(bnss_id, bnss_id)
                bnss = self.bnssIdToBnssDict[bnss_id]
            
                if user_id not in self.usrIdToUsrDict:
                    self.usrIdToUsrDict[user_id] = user(user_id, user_name)    
                usr = self.usrIdToUsrDict[user_id]
            
            
                revw = review(review_id, usr.getId(), bnss.getId(), stars, date_object)
            
                if review_id in self.reviewIdToReviewDict:
                    print 'already there',review_id
                
                self.reviewIdToReviewDict[review_id] = revw
            
                
        with open(reviewFile, 'r') as f:
            lines = f.read().splitlines()
            for line in lines:
                line = line.replace('\,','')
                row = line.split(',')
                if len(row) != len(COLS):
                    continue
                bnss_id = row[0]
                review_id = row[1]
                review_id = (bnss_id, review_id)
                review_text = row[3]
                if review_id not in self.reviewIdToReviewDict:
                    #print 'Not Present', review_id
                    continue
                
                self.reviewIdToReviewDict[review_id].setReviewText(review_text)
        
        return (self.usrIdToUsrDict, self.bnssIdToBnssDict, self.reviewIdToReviewDict)
        
    def readDataWithPandas(self, reviewFolder):
        reviewMetaFile = join(reviewFolder, META_FILE)
        
        df1 = pd.read_csv(reviewMetaFile,escapechar='\\',header=None,\
                              dtype=object)
        
        #df1 =  df1.dropna(axis=0, how='all')
        
        reviewFile = join(reviewFolder, REVIEW_FILE)
        
        df2 = pd.read_csv(reviewFile,escapechar='\\',header=None,\
                              dtype=object, names = COLS)
         
        df2 = df2.dropna(axis=0, how='all')
        print df1.describe()
        
        for index,row in df1.iterrows():
            print index
            print row
            break
        
        for row in df1.itertuples():
            print row
            break
        
        sys.exit()
     
        for row in df1.itertuples():
            print row
            row = row[0]
            bnss_id = row[META_IDX_DICT[META_BNSS_ID]]
            user_id = row[META_IDX_DICT[META_USER_ID]]
            user_name = row[META_IDX_DICT[META_USER_NAME]]
            review_id = row[META_IDX_DICT[META_REVIEW_ID]]
            stars = row[META_IDX_DICT[META_STARS]]
            review_date = row[META_IDX_DICT[META_DATE]]
            
            review_id = (bnss_id, review_id)
            
            try :
                date_object = dateutil.parser.parse(review_date)
                date_object = date_object.date()
            except:
                e = sys.exc_info()[0]
                print e
                continue
            try:
                stars = float(stars)
            except:
                e = sys.exc_info()[0]
                print e
                continue
            
            if bnss_id not in self.bnssIdToBnssDict:
                self.bnssIdToBnssDict[bnss_id] = business(bnss_id, bnss_id)
            bnss = self.bnssIdToBnssDict[bnss_id]
            
            if user_id not in self.usrIdToUsrDict:
                self.usrIdToUsrDict[user_id] = user(user_id, user_name)    
            usr = self.usrIdToUsrDict[user_id]
            
            
            revw = review(review_id, usr.getId(), bnss.getId(), stars, date_object)
            
            if review_id in self.reviewIdToReviewDict:
                print 'already there',review_id
                
            self.reviewIdToReviewDict[review_id] = revw
        
            
        for row2 in df2.itertuples():
            bnss_id = row2[1]
            review_id = row2[2]
            review_id = (bnss_id, review_id)
            review_text = row2[4]
            if review_id not in self.reviewIdToReviewDict:
                #print 'Not Present', review_id
                continue
                
            self.reviewIdToReviewDict[review_id].setReviewText(review_text)
        
        
        return (self.usrIdToUsrDict, self.bnssIdToBnssDict, self.reviewIdToReviewDict)