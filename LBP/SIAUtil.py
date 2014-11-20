'''
Created on Nov 3, 2014

@author: Santhosh Kumar Manavasi Lakshminarayanan, Sarath Rami
'''
import networkx as nx
import numpy
from numpy import float32
import math

'''
Node Types
'''
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

REVIEW_TYPE_GOOD = 0
REVIEW_TYPE_BAD = 1

'''
Compatibility Potential
'''
episolon = math.pow(10, -6)
compatabilityPotential = numpy.ones(shape=(2,2), dtype=float32)
def initialiazePotential():
    for i in range(0,2):
        for j in range(0,2):
            for k in range(0,2):
                output = 0
                if i == REVIEW_TYPE_GOOD:
                    if j == USER_TYPE_HONEST:
                        if k == PRODUCT_TYPE_GOOD:
                            output = episolon
                        else:
                            output = 1-episolon
                    else:
                        if k == PRODUCT_TYPE_GOOD:
                            output = 1-(2*episolon)
                        else:
                            output = (2*episolon)
                else:
                    if j == USER_TYPE_HONEST:
                        if k == PRODUCT_TYPE_GOOD:
                            output = 1-episolon
                        else:
                            output = episolon
                    else:
                        if k == PRODUCT_TYPE_GOOD:
                            output = (2*episolon)
                        else:
                            output = 1-(2*episolon)
                compatabilityPotential[i][j][k] = output
                    

# class CustomGraph(nx.Graph):
#     pass
        

'''
  SIAObject to be used as Graph node
'''

class SIAObject(object):
    def __init__(self, score=(0.5, 0.5), NODE_TYPE=USER):
        self.score = score
        self.messages = dict()
        self.nodeType = NODE_TYPE
    
    def addMessages(self, node, message):
        self.messages[(self,node)] = message
    
    def calculateAndSendMessagesToNeighBors(self, neighbors):
        for neighbor in neighbors:
            message = self.calculateMessageForNeighbor(neighbor);
            neighbor.addMessages(self, message)
            
    def getScore(self):
        return self.score
    
    def getNodeType(self):
        return self.nodeType
    
    def getNormalizingValue(self, v):
        norm=v.sum()
        return norm
    
    def normalizeMessages(self):
        normalizedMessages = numpy.array(self.messages.values())
        normalizingValue = self.getNormalizingValue(normalizedMessages)
        for key in self.messages.keys():
            self.messages[key] = self.messages[key]/normalizingValue

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
    
    
    def calculateMessageForNeighbor(self, neighbor):
        allOtherNeighborMessageMultiplication = 1;
        for messageKey in self.messages.keys():
            if messageKey != (self,neighbor): #leaving the neighbor for which we are going to send message
                message= self.messages[messageKey]
                allOtherNeighborMessageMultiplication = allOtherNeighborMessageMultiplication*message
        scoreAddition= ((self.score[USER_TYPE_FRAUD]*allOtherNeighborMessageMultiplication),
                        (self.score[USER_TYPE_HONEST]*allOtherNeighborMessageMultiplication))
        return scoreAddition
    
    def calculateBeliefVals(self):
        allNeighborMessageMultiplication = 1
        for messageKey in self.messages.keys():
            message= self.messages[messageKey]
            allNeighborMessageMultiplication = allNeighborMessageMultiplication*message
        scoreAdditionHonest=0
        scoreAdditionFraud=0
        scoreAdditionHonest= scoreAdditionHonest+(self.score[USER_TYPE_HONEST]*allNeighborMessageMultiplication)
        scoreAdditionFraud= scoreAdditionFraud+(self.score[USER_TYPE_FRAUD]*allNeighborMessageMultiplication)
        return (scoreAdditionFraud,scoreAdditionHonest)

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
    
    def calculateMessageForNeighbor(self, neighbor):
        allOtherNeighborMessageMultiplication = 1;
        for messageKey in self.messages.keys():
            if messageKey != (self,neighbor):
                message= self.messages[messageKey]
                allOtherNeighborMessageMultiplication = allOtherNeighborMessageMultiplication*message
        scoreAddition=0
        for productType in PRODUCT_TYPES:
            scoreAddition= scoreAddition+(self.score[productType]*allOtherNeighborMessageMultiplication)
        return scoreAddition
    
    def calculateBeliefVals(self):
        allNeighborMessageMultiplication = 1;
        for messageKey in self.messages.keys():
            message= self.messages[messageKey]
            allNeighborMessageMultiplication = allNeighborMessageMultiplication*message
        scoreAdditionGood=0
        scoreAdditionBad=0
        scoreAdditionGood= scoreAdditionGood+(self.score[PRODUCT_TYPE_GOOD]*allNeighborMessageMultiplication)
        scoreAdditionBad= scoreAdditionBad+(self.score[PRODUCT_TYPE_BAD]*allNeighborMessageMultiplication)
        return (scoreAdditionBad,scoreAdditionGood)

class review(SIALink):
    def __init__(self, _id, rating, txt='', recommended=True):
        super(review, self).__init__()
        self.id = _id
        self.rating = rating
        #self.usr = usr
        #self.bn = bn
        self.text = txt
        self.recommended = recommended
        
    def getRating(self):
        return self.rating
    
    def getId(self):
        return self.id
    
#     def getUsr(self):
#         return self.usr
#     
#     def getBusiness(self):
#         return self.bn
    
    def getReviewText(self):
        return self.text
    
    def isRecommended(self):
        return self.recommended
    
