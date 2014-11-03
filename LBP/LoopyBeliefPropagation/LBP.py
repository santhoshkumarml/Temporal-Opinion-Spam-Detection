'''
@author: Santhosh Kumar Manavasi Lakshminaryanan
'''

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

'''
  Class Node to be used in Graph
'''
class node(object):
    def __init__(self, score=(0.5, 0.5), neighbors=[], NODE_TYPE = USER):
        self.score = score
        self.neighbors=neighbors
        self.nodeType = NODE_TYPE
        self.messages = dict()
        
    def getNeighbors(self):
        return self.neighbors
    
    def addNeighbor(self, node2):
        self.neighbors.append(node2)
    
    def removeNeighbor(self, node2):
        self.neighbors.remove(node2)
    
    def addMessages(self, node, message):
        self.messages[(self,node)] = message
        
    def calculateMessageForNeighbor(self, neighbor):
        allOtherNeighborMessageMultiplication = 1;
        for messageKey in self.messages.keys():
            if messageKey != (self,neighbor):
                message= self.messages[messageKey]
                allOtherNeighborMessageMultiplication = allOtherNeighborMessageMultiplication*message
        scoreAddition =0
        if self.nodeType == USER:
            for userType in USER_TYPES:
                scoreAddition+= (self.score[userType]*allOtherNeighborMessageMultiplication)
        else:
            for productType in PRODUCT_TYPES:
                scoreAddition+= (self.score[productType]*allOtherNeighborMessageMultiplication)
        return scoreAddition
        
    def calculateBeliefVals(self):
        allNeighborMessageMultiplication = 1;
        for messageKey in self.messages.keys():
            message= self.messages[messageKey]
            allNeighborMessageMultiplication = allNeighborMessageMultiplication*message
        scoreAddition =(0,0)
        if self.nodeType == USER:
            scoreAddition[USER_TYPE_HONEST]+= (self.score[USER_TYPE_HONEST]*allNeighborMessageMultiplication)
            scoreAddition[USER_TYPE_FRAUD]+= (self.score[USER_TYPE_FRAUD]*allNeighborMessageMultiplication)
        else:
            scoreAddition[PRODUCT_TYPE_GOOD]+= (self.score[PRODUCT_TYPE_GOOD]*allNeighborMessageMultiplication)
            scoreAddition[PRODUCT_TYPE_BAD]+= (self.score[PRODUCT_TYPE_BAD]*allNeighborMessageMultiplication)
        return scoreAddition
    
    def calculateAndSendMessagesToNeighBors(self):
        for neighbor in self.getNeighbors():
            message = self.calculateMessageForNeighbor(neighbor);
            neighbor.addMessages(self, message)
            
    def getScore(self):
        return self.score
    
    def getNodeType(self):
        return self.nodeType
    
'''
 Class UnDirected Graph to run Loopy Belief Propagation
'''
class UnDirectedGraph(object):
    def __init__(self, nodes=[], edges=[]):
        self.nodes = nodes
        self.edges = edges
        
    def add_node(self, node):
        self.nodes.append(node)
    
    def add_edge(self, user, product):
        self.edges.append((user,product))
        user.addNeighbor(product)
        product.addNeighbor(user)
        
    def delete_node(self, node):
        self.nodes.remove(node)
    
    def delete_edge(self, user, product):
        self.edges.remove((user,product))
        user.removeNeighbor(product)
        product.removeNeighbor(user)

    def getNodes(self):
        return self.nodes
    
    def getEdges(self):
        return self.edges
'''
 Loopy Belief Propagation
'''
class LBP(object):
    def __init__(self, dg):
        self.dg = dg
        
    def doBeliefPropagation(self, flipFromUsersToProducts, saturation):
        if saturation:
            if flipFromUsersToProducts:
                for user in self.dg.getNodes():
                    if user.getNodeType() == USER:
                        user.calculateAndSendMessagesToNeighBors()
                self.doBeliefPropagation(not flipFromUsersToProducts, saturation)
            else:
                for product in self.dg.getNodes():
                    if product.getNodeType() == PRODUCT:
                        product.calculateAndSendMessagesToNeighBors()
                self.doBeliefPropagation(not flipFromUsersToProducts, saturation-1)