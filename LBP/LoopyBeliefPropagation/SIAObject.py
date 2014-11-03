'''
Created on Nov 3, 2014

@author: Santhosh Kumar Manavasi Lakshminarayanan, Sarath Rami
'''
import networkx as nx

'''
Node Types
'''
USER = 0
PRODUCT = 1

'''
User Types
'''
USER_TYPE_FRAUD = 0
USER_TYPE_HONEST = 1
USER_TYPES = {USER_TYPE_HONEST, USER_TYPE_FRAUD}
'''
Product Types
'''
PRODUCT_TYPE_BAD = 0
PRODUCT_TYPE_GOOD = 1
PRODUCT_TYPES = {PRODUCT_TYPE_GOOD, PRODUCT_TYPE_BAD}

'''
Review Types
'''
REVIEW_TYPE_FAKE = 0
REVIEW_TYPE_REAL = 1



class CustomGraph(nx.Graph):
    pass
        

'''
  SIAObject to be used as Graph node
'''

class SIAObject(object):
    def __init__(self, graph, score=(0.5, 0.5), NODE_TYPE=USER):
        self.score = score
        self.messages = dict()
        self.graph = graph
        self.nodeType = NODE_TYPE
        
    def getNeighbors(self):
        return self.graph.neighbors(self)
    
    def addMessages(self, node, message):
        self.messages[(self,node)] = message
    
    def calculateAndSendMessagesToNeighBors(self):
        for neighbor in self.getNeighbors():
            message = self.calculateMessageForNeighbor(neighbor);
            neighbor.addMessages(self, message)
            
    def getScore(self):
        return self.score
    
    def getNodeType(self):
        return self.nodeType
    
    
class user(SIAObject):
    def __init__(self, id, name, graph, score=(0.5,0.5)):
        super(user, self).__init__(graph, score, USER)
        self.id = id
        self.name = name
    
    def calculateMessageForNeighbor(self, neighbor):
        allOtherNeighborMessageMultiplication = 1;
        for messageKey in self.messages.keys():
            if messageKey != (self,neighbor):
                message= self.messages[messageKey]
                allOtherNeighborMessageMultiplication = allOtherNeighborMessageMultiplication*message
        scoreAddition=0
        for userType in USER_TYPES:
            scoreAddition+= (self.score[userType]*allOtherNeighborMessageMultiplication)
        return scoreAddition
    
    def calculateBeliefVals(self):
        allNeighborMessageMultiplication = 1;
        for messageKey in self.messages.keys():
            message= self.messages[messageKey]
            allNeighborMessageMultiplication = allNeighborMessageMultiplication*message
        scoreAddition=(0,0)
        scoreAddition[USER_TYPE_HONEST]+= (self.score[USER_TYPE_HONEST]*allNeighborMessageMultiplication)
        scoreAddition[USER_TYPE_FRAUD]+= (self.score[USER_TYPE_FRAUD]*allNeighborMessageMultiplication)
        return scoreAddition

class business(SIAObject):
    def __init__(self, id, name, rating=2.5, url=None, graph, score=(0.5,0.5)):
        super(business, self).__init__(graph, score, PRODUCT)
        self.id = id
        self.name = name
        self.rating = rating
        self.url = url
    
    def calculateMessageForNeighbor(self, neighbor):
        allOtherNeighborMessageMultiplication = 1;
        for messageKey in self.messages.keys():
            if messageKey != (self,neighbor):
                message= self.messages[messageKey]
                allOtherNeighborMessageMultiplication = allOtherNeighborMessageMultiplication*message
        scoreAddition=0
        for productType in PRODUCT_TYPES:
            scoreAddition+= (self.score[productType]*allOtherNeighborMessageMultiplication)
        return scoreAddition
    
    def calculateBeliefVals(self):
        allNeighborMessageMultiplication = 1;
        for messageKey in self.messages.keys():
            message= self.messages[messageKey]
            allNeighborMessageMultiplication = allNeighborMessageMultiplication*message
        scoreAddition=(0,0)
        scoreAddition[PRODUCT_TYPE_GOOD]+= (self.score[PRODUCT_TYPE_GOOD]*allNeighborMessageMultiplication)
        scoreAddition[PRODUCT_TYPE_BAD]+= (self.score[PRODUCT_TYPE_BAD]*allNeighborMessageMultiplication)
        return scoreAddition

class review:
    def __init__(self, id, rating, usr, bn, txt='', recommended=True):
        self.id = id
        self.rating = rating
        self.usr = usr
        self.bn = bn
        self.text = txt
        self.recommended = recommended
    
