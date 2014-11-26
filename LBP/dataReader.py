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
    parentUserIdToUserDict = dict()
    parentBusinessIdToBusinessDict = dict()
    parent_reviews = []
    isBusinessAlreadyPresent = False
    with open(inputFileName) as f:
        for line in f:
            if re.match('^B=', line):
                exec(line)
                #print 'B = ', B
                isBusinessAlreadyPresent = False
                if B[0] in parentBusinessIdToBusinessDict:
                    #business_already_present i am skipping
                    isBusinessAlreadyPresent=True
                bnss = business(B[0],B[1],B[2],B[4])
                parentBusinessIdToBusinessDict[bnss.getId()] = bnss
            elif re.match('^R=', line):
                exec(line)
                if isBusinessAlreadyPresent:
                    #business_already_present i am skipping
                    continue
                #print 'R = ', R
                for recoRev in R:
                    usr = user(recoRev[1], recoRev[2])
                    dictUsr = parentUserIdToUserDict.get(usr.getId())
                    if not dictUsr:
                        parentUserIdToUserDict[usr.getId()] = usr
                        dictUsr = usr
                    revw = review(recoRev[0], dictUsr.getId(), bnss.getId(), recoRev[3],recoRev[4], recoRev[5], True)
                    parent_reviews.append(revw)
            elif re.match('^NR=', line):
                exec(line)
                if isBusinessAlreadyPresent:
                    #business_already_present i am skipping
                    continue
                #print 'NR = ', NR
                for noRecoRev in NR:
                    usr = user(noRecoRev[1], noRecoRev[2])
                    dictUsr = parentUserIdToUserDict.get(usr.getId())
                    if not dictUsr:
                        parentUserIdToUserDict[usr.getId()] = usr
                        dictUsr = usr
                    revw = review(noRecoRev[0], dictUsr.getId(), bnss.getId(), noRecoRev[3], noRecoRev[4], noRecoRev[5], False)
                    parent_reviews.append(revw)
    return (parentUserIdToUserDict,parentBusinessIdToBusinessDict,parent_reviews)