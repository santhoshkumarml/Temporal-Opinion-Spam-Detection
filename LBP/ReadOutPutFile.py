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
            if re.match('^fakeUsers', line):
                exec(line)
            if re.match('^honestUsers', line):
                pass
            if re.match('^badProducts', line):
                pass
            if re.match('^goodProducts', line):
                pass
            if re.match('^fakeReviews', line):
                pass
            if re.match('^realReviews', line):
                pass