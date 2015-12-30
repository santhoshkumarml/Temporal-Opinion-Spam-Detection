'''
Created on Dec 30, 2015

@author: santhosh
'''
import os

POS_REVW_FILE = 'pos_reviews.txt'
NEG_REVW_FILE = 'neg_reviews.txt'
ALL_REVIEWS_FILE = 'all_reviews.txt'

def writeReviewTextInFile(reviews, review_file_name, fdr):
    with open(os.path.join(fdr, review_file_name), 'w') as f:
        for revw in reviews:
            f.write(revw.getReviewText())
            f.write('\n')

def runPhraseFilterAndSeperate(reviews, phrase, fdr):
    filtered_reviews = [revw for revw in reviews if phrase in revw.getReviewText()]
    pos_filtered_reviews = [revw for revw in filtered_reviews if revw.getRating()>=4.0]
    neg_filtered_reviews = [revw for revw in filtered_reviews if revw.getRating()<=2.0]
    writeReviewTextInFile(filtered_reviews, ALL_REVIEWS_FILE, fdr)
    writeReviewTextInFile(pos_filtered_reviews, POS_REVW_FILE, fdr)
    writeReviewTextInFile(neg_filtered_reviews, NEG_REVW_FILE, fdr)

