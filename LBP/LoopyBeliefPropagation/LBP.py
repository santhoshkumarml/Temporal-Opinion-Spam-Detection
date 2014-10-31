'''
@author: Santhosh Kumar Manavasi Lakshminaryanan
'''
from math import exp

'''
Node Types
'''
USER = 0
PRODUCT = 1

'''
User Types
'''
USER_TYPE_FRAUD = -1
USER_TYPE_HONEST = 1

'''
Product Types
'''
PRODUCT_TYPE_BAD = -1
PRODUCT_TYPE_GOOD = 1

'''
Review Types
'''
REVIEW_TYPE_FAKE = -1
REVIEW_TYPE_REAL = 1

'''
  Node Util to be used in Graph
'''
class node(object):
    def __init__(self, score=1, neighbors=[], NODE_TYPE = USER):
        self.score = score
        self.neighbors=neighbors
        self.nodeType = NODE_TYPE
        self.beliefVals = []
        
    def getNeighbors(self):
        return self.neighbors
    
    def addNeighbor(self, node2):
        self.neighbors.append(node2)
    
    def removeNeighbor(self, node2):
        self.neighbors.remove(node2)
    
    def addBeliefVals(self, node, val):
        self.beliefVals[(self,node)] = val
        
    def calculateBelief(self, neighbor):
        beliefVal = 1
        #beliefVal = alpha
        
        return beliefVal
    
    def calculateAndSendBeliefsToNeighBors(self):
        for neighbor in self.getNeighbors():
            beliefVal = self.calculateBelief(neighbor);
            neighbor.addBeliefVals(beliefVal)
            
    def getScore(self):
        return self.score
    
    def getNodeType(self):
        return self.nodeType
    
'''
 Directed Graph Util to run Loopy Belief Propagation
'''
class UnDirectedGraph(object):
    def __init__(self, nodes=[], edges=[]):
        self.nodes = nodes
        self.edges = edges
        
    def add_node(self, node):
        self.nodes.append(node)
    
    def add_edge(self, user, product, score=1):
        self.edges[(user,product)]=score
        #self.edges[(product,user)]=score
        user.addNeighbor(product)
        product.addNeighbor(user)
        
    def delete_node(self, node):
        self.nodes.remove(node)
    
    def delete_edge(self, user, product):
        del(self.edges[(user,product)])
        user.removeNeighbor(product)
        product.removeNeighbor(user)

    def getNodes(self):
        return self.nodes
    
    def getEdges(self):
        return self.edges
'''
 Loopy belief Propagation
'''
class LBP(object):
    def __init__(self, dg):
        self.dg = dg
        
    def doBeliefPropagation(self, flipFromUsersToProducts, saturation):
        if saturation:
            if flipFromUsersToProducts:
                for user in self.dg.getNodes():
                    if user.getNodeType() == USER:
                        user.calculateAndSendBeliefsToNeighBors()
                self.doBeliefPropagation(not flipFromUsersToProducts, saturation)
            else:
                for product in self.dg.getNodes():
                    if product.getNodeType() == PRODUCT:
                        product.calculateAndSendBeliefsToNeighBors()
                self.doBeliefPropagation(not flipFromUsersToProducts, saturation-1)