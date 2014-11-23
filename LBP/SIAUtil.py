'''
Created on Nov 3, 2014

@author: Santhosh Kumar Manavasi Lakshminarayanan, Sarath Rami
'''
'''
Node Types
'''

import math
from numpy import float32
import numpy


USER = 'USER'
PRODUCT = 'PRODUCT'

'''
User Types
'''
USER_TYPE_FRAUD = 0
USER_TYPE_HONEST = 1
USER_TYPES = {USER_TYPE_FRAUD, USER_TYPE_HONEST}
'''
Product Types
'''
PRODUCT_TYPE_BAD = 0
PRODUCT_TYPE_GOOD = 1
PRODUCT_TYPES = {PRODUCT_TYPE_BAD, PRODUCT_TYPE_GOOD}

'''
Review Types
'''
REVIEW_TYPE_FAKE = 0
REVIEW_TYPE_REAL = 1

REVIEW_TYPE_NEGATIVE = 0
REVIEW_TYPE_POSITIVE = 1

REVIEW_EDGE_DICT_CONST = 'review'
'''
Compatibility Potential
'''
EPISOLON = math.pow(10, -4)
COMP_POT = numpy.ones(shape=(2,2,2), dtype=float32)
def init_COMP_POT():
    for i in range(0,2):
        for j in range(0,2):
            for k in range(0,2):
                output = 0
                if i == REVIEW_TYPE_NEGATIVE:
                    if j == USER_TYPE_HONEST:
                        if k == PRODUCT_TYPE_GOOD:
                            output = EPISOLON
                        else:
                            output = 1-EPISOLON
                    else:
                        if k == PRODUCT_TYPE_GOOD:
                            output = 1-(2*EPISOLON)
                        else:
                            output = (2*EPISOLON)
                else:
                    if j == USER_TYPE_HONEST:
                        if k == PRODUCT_TYPE_GOOD:
                            output = 1-EPISOLON
                        else:
                            output = EPISOLON
                    else:
                        if k == PRODUCT_TYPE_GOOD:
                            output = (2*EPISOLON)
                        else:
                            output = 1-(2*EPISOLON)
                COMP_POT[i][j][k] = output
                

init_COMP_POT()

'''
  SIAObject to be used as Graph node
'''

class SIAObject(object):
    def __init__(self, score=(0.5, 0.5), NODE_TYPE=USER):
        self.score = score
        self.messages = dict()
        self.nodeType = NODE_TYPE

    def getMessageFromNeighbor(self, neighbor):
        return self.messages[neighbor]

    def addMessages(self, node, message):
        hasChanged = False
        message = self.normalizeMessage(message)
        if node not in self.messages or self.messages[node] != message:
            self.messages[node] = message
            hasChanged = True
        return hasChanged
    
    def calculateAndSendMessagesToNeighBors(self, neighborsWithEdges):
        hasAnyMessageChanged = False
        for neighborWithEdge in neighborsWithEdges:
            message = self.calculateMessageForNeighbor(neighborWithEdge);
            if(neighborWithEdge[0].addMessages(self, message)):
                hasAnyMessageChanged = True
        return hasAnyMessageChanged
            
    def getScore(self):
        return self.score
    
    def getNodeType(self):
        return self.nodeType

    def normalizeMessage(self, message):
        normalizingValue = message[0]+message[1]
        message = (message[0]/normalizingValue, message[1]/normalizingValue)
        return message

class SIALink(object):
    def __init__(self, score=(0.5, 0.5)):
        self.score = score
            
    def getScore(self):
        return self.score
    
class user(SIAObject):
    def __init__(self, _id, name, score=(0.5,0.5)):
        super(user, self).__init__(score, USER)
        self.id = _id
        self.name = name
    
    def getName(self):
        return self.name
    
    def getId(self):
        return self.id
    
    
    def calculateMessageForNeighbor(self, neighborWithEdge):
        allOtherNeighborMessageMultiplication = (1,1)
        (neighbor, edge) = neighborWithEdge
        for messageKey in self.messages.keys():
            if messageKey != neighbor:
                message= self.messages[messageKey]
                allOtherNeighborMessageMultiplication = \
                (allOtherNeighborMessageMultiplication[USER_TYPE_FRAUD]*message[USER_TYPE_FRAUD] , \
                 allOtherNeighborMessageMultiplication[USER_TYPE_HONEST]*message[USER_TYPE_HONEST])
        scoreAddition = (0,0)
        review = edge[REVIEW_EDGE_DICT_CONST]
        for userType in USER_TYPES:
            scoreAddition=\
             (scoreAddition[0]+(COMP_POT[review.getReviewSentiment()][userType][PRODUCT_TYPE_BAD]*self.score[userType]*allOtherNeighborMessageMultiplication[userType]),\
             scoreAddition[1]+(COMP_POT[review.getReviewSentiment()][userType][PRODUCT_TYPE_GOOD]*self.score[userType]*allOtherNeighborMessageMultiplication[userType]))
        return scoreAddition
    
    def calculateBeliefVals(self):
        allNeighborMessageMultiplication = (1,1)
        for messageKey in self.messages.keys():
            message= self.messages[messageKey]
            allNeighborMessageMultiplication = \
                (allNeighborMessageMultiplication[USER_TYPE_FRAUD]*message[USER_TYPE_FRAUD] , \
                 allNeighborMessageMultiplication[USER_TYPE_HONEST]*message[USER_TYPE_HONEST])
        normalizingValue = (self.score[USER_TYPE_FRAUD]*allNeighborMessageMultiplication[USER_TYPE_FRAUD])+\
        (self.score[USER_TYPE_HONEST]*allNeighborMessageMultiplication[USER_TYPE_HONEST])
        self.score = ((self.score[USER_TYPE_FRAUD]*allNeighborMessageMultiplication[USER_TYPE_FRAUD])/normalizingValue, \
                (self.score[USER_TYPE_HONEST]*allNeighborMessageMultiplication[USER_TYPE_HONEST])/normalizingValue)

class business(SIAObject):
    def __init__(self, _id, name, rating=2.5, url=None, score=(0.5,0.5)):
        super(business, self).__init__(score, PRODUCT)
        self.id = _id
        self.name = name
        self.rating = rating
        self.url = url
        
    def getName(self):
        return self.name
    
    def getId(self):
        return self.id
    
    def getRating(self):
        return self.rating
    
    def getUrl(self):
        return self.url
    
    def calculateMessageForNeighbor(self, neighborWithEdge):
        allOtherNeighborMessageMultiplication = (1,1)
        (neighbor, edge) = neighborWithEdge
        for messageKey in self.messages.keys():
            if messageKey != neighbor:
                message= self.messages[messageKey]
                allOtherNeighborMessageMultiplication = \
                (allOtherNeighborMessageMultiplication[PRODUCT_TYPE_BAD]*message[PRODUCT_TYPE_BAD] , \
                 allOtherNeighborMessageMultiplication[PRODUCT_TYPE_GOOD]*message[PRODUCT_TYPE_GOOD])
        review = edge[REVIEW_EDGE_DICT_CONST]
        scoreAddition = (0,0)
        for productType in PRODUCT_TYPES:
            scoreAddition=\
             (scoreAddition[0]+(COMP_POT[review.getReviewSentiment()][USER_TYPE_FRAUD][productType]*self.score[productType]*allOtherNeighborMessageMultiplication[productType]),\
             scoreAddition[1]+(COMP_POT[review.getReviewSentiment()][USER_TYPE_HONEST][productType]*self.score[productType]*allOtherNeighborMessageMultiplication[productType]))
        return scoreAddition
    
    def calculateBeliefVals(self):
        allNeighborMessageMultiplication = (1,1)
        for messageKey in self.messages.keys():
            message= self.messages[messageKey]
            allNeighborMessageMultiplication = \
                (allNeighborMessageMultiplication[PRODUCT_TYPE_BAD]*message[PRODUCT_TYPE_BAD] , \
                 allNeighborMessageMultiplication[PRODUCT_TYPE_GOOD]*message[PRODUCT_TYPE_GOOD])
        normalizingValue = (self.score[PRODUCT_TYPE_BAD]*allNeighborMessageMultiplication[PRODUCT_TYPE_BAD])+ \
                (self.score[PRODUCT_TYPE_GOOD]*allNeighborMessageMultiplication[PRODUCT_TYPE_GOOD])
        self.score = ((self.score[PRODUCT_TYPE_BAD]*allNeighborMessageMultiplication[PRODUCT_TYPE_BAD])/normalizingValue,\
                (self.score[PRODUCT_TYPE_GOOD]*allNeighborMessageMultiplication[PRODUCT_TYPE_GOOD])/normalizingValue)

class review(SIALink):
    def __init__(self, _id, usr, bn, rating, txt='', recommended=True):
        super(review, self).__init__()
        self.id = _id
        self.rating = rating
        self.usr = usr
        self.bn = bn
        self.text = txt
        self.recommended = recommended
        
    def getRating(self):
        return self.rating
    
    def getId(self):
        return self.id
    
    def getReviewSentiment(self):
        if self.getRating()>=3.0:
            return REVIEW_TYPE_POSITIVE
        else:
            return REVIEW_TYPE_NEGATIVE
    
    def getUser(self):
        return self.usr
          
    def getBusiness(self):
        return self.bn
      
    def getReviewText(self):
        return self.text
    
    def isRecommended(self):
        return self.recommended
    
