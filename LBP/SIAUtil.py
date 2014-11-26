'''
Created on Nov 3, 2014

@author: Santhosh Kumar Manavasi Lakshminarayanan, Sarath Rami
'''
from datetime import datetime, date, timedelta
from copy import deepcopy
'''
Node Types
'''
import numpy
import networkx
import re
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
REVIEW_TYPES = {REVIEW_TYPE_FAKE, REVIEW_TYPE_REAL}


REVIEW_TYPE_NEGATIVE = 0
REVIEW_TYPE_POSITIVE = 1

REVIEW_EDGE_DICT_CONST = 'review'
'''
Compatibility Potential
'''
EPISOLON = 10**-4
#COMP_POT = [[[0.0 for productType in PRODUCT_TYPES] for userType in USER_TYPES] for reviewType in REVIEW_TYPES]
COMP_POT = numpy.zeros(shape=(2,2,2),dtype=numpy.float32)
def init_COMP_POT():
    for reviewType in REVIEW_TYPES:
        for userType in USER_TYPES:
            for productType in PRODUCT_TYPES:
                output = 0
                if reviewType == REVIEW_TYPE_NEGATIVE:
                    if userType == USER_TYPE_HONEST:
                        if productType == PRODUCT_TYPE_GOOD:
                            output = EPISOLON
                        else:
                            output = 1-EPISOLON
                    else:
                        if productType == PRODUCT_TYPE_GOOD:
                            output = 1-(2*EPISOLON)
                        else:
                            output = (2*EPISOLON)
                else:
                    if userType == USER_TYPE_HONEST:
                        if productType == PRODUCT_TYPE_GOOD:
                            output = 1-EPISOLON
                        else:
                            output = EPISOLON
                    else:
                        if productType == PRODUCT_TYPE_GOOD:
                            output = 2*EPISOLON
                        else:
                            output = 1-(2*EPISOLON)
                            
                COMP_POT[reviewType][userType][productType] = output

init_COMP_POT()
# print ((COMP_POT[0][0][0]*0.5)+(COMP_POT[0][0][1]*0.5),(COMP_POT[0][1][0]*0.5)+(COMP_POT[0][1][1]*0.5))
# print ((COMP_POT[0][0][0]*0.5)+(COMP_POT[0][1][0]*0.5),(COMP_POT[0][0][1]*0.5)+(COMP_POT[0][1][1]*0.5))
# print ((COMP_POT[1][0][0]*0.5)+(COMP_POT[1][0][1]*0.5),(COMP_POT[1][1][0]*0.5)+(COMP_POT[1][1][1]*0.5))
# print ((COMP_POT[1][0][0]*0.5)+(COMP_POT[1][1][0]*0.5),(COMP_POT[1][0][1]*0.5)+(COMP_POT[1][1][1]*0.5))
'''
  SIAObject to be used as Graph node
'''

class SIAObject(object):
    def __init__(self, score=(0.5, 0.5), NODE_TYPE=USER):
        self.score = score
        self.messages = dict()
        self.nodeType = NODE_TYPE
    
    def reset(self):
        self.messages.clear()
        self.score = (0.5,0.5)

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
        changedNeighbors = []
        for neighborWithEdge in neighborsWithEdges:
            (neighbor,edge) = neighborWithEdge
            message = self.calculateMessageForNeighbor(neighborWithEdge);
            if(neighbor.addMessages(self, message)):
                changedNeighbors.append(neighbor)
        return changedNeighbors
            
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
    def __init__(self, _id, usrId, bnId, rating, timeOfReview, txt='', recommended=True):
        super(review, self).__init__()
        self.id = _id
        self.rating = float(rating)
        self.usrId = usrId
        self.bnId = bnId
        self.timeOfReview = timeOfReview
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
    
    def getUserId(self):
        return self.usrId
          
    def getBusinessID(self):
        return self.bnId
    
    def getTimeOfReview(self):
        return self.timeOfReview
      
    def getReviewText(self):
        return self.text
    
    def isRecommended(self):
        return self.recommended
    
    def calculateBeliefVals(self, user, business):
        self.score = user.getMessageFromNeighbor(business)



class TimeBasedGraph(networkx.Graph):
    def __init__(self, parentUserIdToUserDict=dict(),parentBusinessIdToBusinessDict=dict()):
        super(TimeBasedGraph, self).__init__()
        self.userIdToUserDict = deepcopy(parentUserIdToUserDict)
        self.businessIdToBusinessDict = deepcopy(parentBusinessIdToBusinessDict)
        
    def initialize(self,parentUserIdToUserDict,parentBusinessIdToBusinessDict):
        self.userIdToUserDict = deepcopy(parentUserIdToUserDict)
        self.businessIdToBusinessDict = deepcopy(parentBusinessIdToBusinessDict)
        
    def getUser(self,userId):
        return self.userIdToUserDict[userId]
    
    def getBusiness(self, businessId):
        return self.businessIdToBusinessDict[businessId]
    

def createGraph(parentUserIdToUserDict,parentBusinessIdToBusinessDict,parent_reviews):
    G = TimeBasedGraph(parentUserIdToUserDict, parentBusinessIdToBusinessDict)
    for review in parent_reviews:
        usr = G.getUser(review.getUserId())
        business = G.getBusiness(review.getBusinessID())
        G.add_node(usr)
        G.add_node(business)
        G.add_edge(business, usr, dict({REVIEW_EDGE_DICT_CONST:review}))
    return G
    
    
def createTimeBasedGraph(parentUserIdToUserDict,parentBusinessIdToBusinessDict, parent_reviews, timeSplit ='1-D'):
    if not re.match('[0-9]+-[DMY]', timeSplit):
        print 'Time Increment does not follow the correct Pattern - Time Increment Set to 1 Day'
        timeSplit ='1-D'

    numeric = int(timeSplit.split('-')[0])
    incrementStr = timeSplit.split('-')[1]
    dayIncrement = 1
    if incrementStr=='D':
        dayIncrement = numeric
    elif incrementStr=='M':
        dayIncrement = numeric*30
    else:
        dayIncrement = numeric*365
        
    minDate =  min([date(int(r.getTimeOfReview().split('/')[2]),\
                    int(r.getTimeOfReview().split('/')[0]),\
                     int(r.getTimeOfReview().split('/')[1]))\
                 for r in parent_reviews ])
    maxDate =  max([date(int(r.getTimeOfReview().split('/')[2]),\
                    int(r.getTimeOfReview().split('/')[0]),\
                     int(r.getTimeOfReview().split('/')[1]))\
                 for r in parent_reviews ])
    cross_time_graphs = dict()
    time_key = 0
    while time_key < ((maxDate-minDate+timedelta(dayIncrement))/dayIncrement).days:
        cross_time_graphs[time_key] = TimeBasedGraph(parentUserIdToUserDict, parentBusinessIdToBusinessDict)
        time_key+=1
    for review in parent_reviews:
        reviewDate = date(int(review.getTimeOfReview().split('/')[2]),\
                    int(review.getTimeOfReview().split('/')[0]),\
                     int(review.getTimeOfReview().split('/')[1]))
        timeDeltaKey = ((reviewDate-minDate)/dayIncrement).days
        timeSplittedgraph = cross_time_graphs[timeDeltaKey]
        usr = timeSplittedgraph.getUser(review.getUserId())
        bnss = timeSplittedgraph.getBusiness(review.getBusinessID())
        timeSplittedgraph.add_node(usr)
        timeSplittedgraph.add_node(bnss)
        timeSplittedgraph.add_edge(usr, bnss, dict({REVIEW_EDGE_DICT_CONST:review}))
    return cross_time_graphs