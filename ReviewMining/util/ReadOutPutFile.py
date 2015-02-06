'''
Created on Nov 23, 2014

@author: santhosh
'''
import sys
import re

if __name__ == '__main__':
    inputFileName = sys.argv[1]
    fakeUsers = []
    honestUsers = []
    badProducts = []
    goodProducts = []
    fakeReviews = []
    realReviews = []
    with open(inputFileName) as f:
        for line in f:
            if re.match('^fakeUsers', line) or re.match('^honestUsers', line)\
             or re.match('^badProducts', line) or re.match('^goodProducts', line)\
             or re.match('^fakeReviews', line) or re.match('^realReviews', line):
                exec(line)
    print 'fakeUsers',len(fakeUsers),'honestUsers', len(honestUsers),\
    'badProducts',len(badProducts), 'goodProducts',len(goodProducts),\
    'fakeReviews', len(fakeReviews),'realReviews',len(realReviews)