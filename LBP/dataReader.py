'''
@author: Sarath Rami
@author: Santhosh Kumar Manavasi Lakshminarayanan
'''
######################################################### Initializers

import re

from SIAUtil import user, business, review
B = []
R = []
NR = []
######################################################### METHODS
def parseAndCreateObjects(inputFileName):
    userIdToUserDict = dict()
    businessIdToBusinessDict = dict()
    reviews = []
    with open(inputFileName) as f:
        for line in f:
            if re.match('^B=', line):
                exec(line)
                #print 'B = ', B
                bnss = business(B[0],B[1],B[2],B[4])
                businessIdToBusinessDict[bnss.getId()] = bnss
            elif re.match('^R=', line):
                exec(line)
                #print 'R = ', R
                for recoRev in R:
                    usr = user(recoRev[1], recoRev[2])
                    dictUsr = userIdToUserDict.get(usr.getId())
                    if not dictUsr:
                        userIdToUserDict[usr.getId()] = usr
                        dictUsr = usr
                    revw = review(recoRev[0], dictUsr, bnss, recoRev[3], recoRev[4], True)
                    reviews.append(revw)
            elif re.match('^NR=', line):
                exec(line)
                #print 'NR = ', NR
                for noRecoRev in NR:
                    usr = user(noRecoRev[1], noRecoRev[2])
                    dictUsr = userIdToUserDict.get(usr.getId())
                    if not dictUsr:
                        userIdToUserDict[usr.getId()] = usr
                        dictUsr = usr
                    revw = review(noRecoRev[0], dictUsr, bnss, noRecoRev[3], noRecoRev[4], False)
                    reviews.append(revw)
    return (userIdToUserDict,businessIdToBusinessDict,reviews)